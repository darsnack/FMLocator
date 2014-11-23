# RDSDecoder
# Module for decoding RDS data from a V4L2 compatible FM radio device
#
# Copyright (C) 2010 <andy.buckingham _AT_ thisisglobal.com>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free 
# Software Foundation; either version 2.1 of the License, or (at your option) 
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA


__all__ = ["RDSDecoderError", "RDSDecoderUnavailableError",
           "RDSDecoderListener", "SegmentedString", "RDSDecoder"]


import struct
import threading


# V4L2 offset name values
_V4L2_RDS_OFFSET_NAME_BLOCK_A     = 0
_V4L2_RDS_OFFSET_NAME_BLOCK_B     = 1
_V4L2_RDS_OFFSET_NAME_BLOCK_C     = 2
_V4L2_RDS_OFFSET_NAME_BLOCK_D     = 3
_V4L2_RDS_OFFSET_NAME_BLOCK_ALT_C = 4
_V4L2_RDS_OFFSET_NAME_BLOCK_E     = 5


class RDSDecoderError(StandardError):
    """
    Base class for FMRadio-related exceptions.
    """
    pass

class RDSDecoderUnavailableError(RDSDecoderError):
    """
    Exception to throw if the radio for the RDS Decoder is unavailable.
    """
    pass


class RDSDecoderListener(object):
    """
    This class should be used as a base class for objects registered
    using Decoder.set_listener()
    """
    
    def on_pi_change(self, decoder, pi):
        """
        Called when the PI code changes
        """
        pass
    
    def on_ecc_change(self, decoder, ecc):
        """
        Called when the ECC changes
        """
        pass
    
    def on_ps_change(self, decoder, ps):
        """
        Called when the PS value changes
        """
        pass
    
    def on_rt_change(self, decoder, message):
        """
        Called when a new RadioText message is received
        """
        pass
    
    def on_reset(self, decoder):
        """
        Called when the RDS Decoder is reset, usually when changing the tuner's frequency
        """
        pass
    

class SegmentedString(object):
    """
    Allow string construction to be performed in segments, such as those used
    in RDS for PS and RT
    """
    
    def __init__(self, length = 0):
        self.set_length(length)
        

    def set_length(self, length):
        if not hasattr(self, '__length') or self.__length != length:
            self.value = " " * length
            self.__length = length
            self.__completion = [False] * length
            

    def set_segment(self, offset, chars):
        start = offset * len(chars)
        end = start + len(chars)
        self.value = self.value[0:start] + chars + self.value[end:self.__length]
        self.__completion[start:end] = [True] * len(chars)
        

    def is_complete(self):
        if self.__length != 0:
            return False not in self.__completion
        

class RDSDecoder(object):
    """
    Class for decoding RDS data from a V4L2 FM Radio
    """
    
    def __init__(self, radio):
        
        self.radio = radio
        
        self.__listeners = []
        self.__running = None
        self.__thread = threading.Thread(None, self.__parsing_loop)
        self.__thread.daemon = True
        
        try:
            self.__fd = open(radio.dev, 'r')
        except OSError:
            raise RDSDecoderUnavailableError("Radio device for RDS Decoder is not available.")
        
        self.reset()
        

    def start(self):
        """
        Starts the internal loop which actively consumes and parses received
        RDS content.
        """
        
        if self.__running: return
        
        self.__running = True
        if not self.__thread.is_alive():
            self.__thread.start()
        

    def stop(self):
        """
        Stops the internal loop.
        """ 
        
        if not self.__running: return
        
        self.__running = False
        

    def reset(self):
        """
        Stops the internal loop (if running), sets (or resets) the object
        property default values and then restarts the internal loop.
        """
        
        self.stop()
        
        self.ecc = None
        self.pi = None
        self.ps = None
        self.rt = None
        
        self.__current_group = {}
        self.__ps_segments = SegmentedString(8)
        self.__rt_segments = SegmentedString()
        
        for listener in self.__listeners:
            listener.on_reset(self)
        
        self.start()
        

    def close(self):
        """
        Closes the RDS Decoder
        """
        
        self.stop()
        
        try:
            self.__fd.close()
        except IOError:
            pass
        

    def add_listener(self, listener):
        """
        Adds an optional object of class RDSDecoderListener to a list of
        listeners to be notified as and when RDS-related events occur
        """
        
        self.__listeners.append(listener)
        

    def remove_listener(self, listener):
        """
        Removes object of class RDSDecoderListener from the list of listeners
        to be notified as and when RDS-related events occur
        """
        
        self.__listeners.remove(listener)
        

    def __parsing_loop(self):
        """
        The main internal parsing loop which runs as a thread and actively
        reads RDS data from the device and attempts to decode and parse it.
        """
        
        while self.__running:
            self.__current_group = {}
            
            for i in range(0, 4):
                block = self.__fd.read(3)
                data, info = struct.unpack("HB", block)
                
                checkword = info & 7
                error = (info >> 7) & 1 == 1
                
                if error:
                    self.__current_group = {}
                    continue
                
                if checkword is _V4L2_RDS_OFFSET_NAME_BLOCK_A:
                    self.__decode_block_a(data)
                if checkword is _V4L2_RDS_OFFSET_NAME_BLOCK_B:
                    self.__decode_block_b(data)
                if checkword is _V4L2_RDS_OFFSET_NAME_BLOCK_C:
                    self.__decode_block_c(data)
                if checkword is _V4L2_RDS_OFFSET_NAME_BLOCK_D:
                    self.__decode_block_d(data)

                if not self.__running:
                    break
                

    def __decode_block_a(self, data):
        """
        Logic for decoding Block A of a group.
        This always contains the PI code.
        """
        
        self.__set_pi(hex(data))
        

    def __decode_block_b(self, data):
        """
        Logic for decoding Block B of a group.
        This always contains meta about the group and optionally other data
        dependent on group type.
        """
        
        self.__current_group = {"type":    (data >> 12) & 15,
                                "version": (data >> 11) & 1,
                                "tp":      (data >> 10) & 1 == 1,
                                "pty":     (data >> 5) & 31}
        
        if self.__current_group["type"] is 0:
            self.__current_group["ta"] = (data >> 4) & 1
            self.__current_group["ms"] = (data >> 3) & 1
            self.__current_group["di"] = (data >> 2) & 1
            self.__current_group["segment"] = (data & 3)
        
        if self.__current_group["type"] is 2:
            self.__current_group["radiotext_ab"] = (data >> 4) & 1
            num_chars = 4 if self.__current_group["version"] else 2
            self.__current_group["segment"] = (data & 15) * num_chars
            

    def __decode_block_c(self, data):
        """
        Logic for decoding Block C of a group.
        Use varies dependent on group type.
        """
        
        try:
            if self.__current_group["version"] is 0:
                if self.__current_group["type"] is 1:
                    variant = (data >> 12) & 7
                    if variant == 0:
                        ecc = data & 255
                        self.__set_ecc(hex(ecc))
                
                if self.__current_group["type"] is 2:
                    chars = chr((data >> 8) & 255) + chr(data & 255)
                    segment = self.__current_group["segment"]
                    self.__rt_segments.set_segment(segment, chars)
                    terminator = chr(13) 
                    if terminator in chars:
                        msg = self.__rt_segments.value.replace(terminator, '')
                        self.__set_rt(msg)
                
            elif self.__current_group["version"] is 1:
                self.__set_pi(hex(data))
        
        except KeyError:
            pass
            

    def __decode_block_d(self, data):
        """
        Logic for decoding Block D of a group.
        Use varies dependent on group type.
        """
        
        try:
            if self.__current_group["type"] is 0:
                segment = self.__current_group["segment"]
                chars = chr((data >> 8) & 255) + chr(data & 255)
                self.__ps_segments.set_segment(segment, chars)
                if self.__ps_segments.is_complete():
                    self.__set_ps(self.__ps_segments.value)
            elif self.__current_group["type"] is 2:
                segment = self.__current_group["segment"]
                offset = 2 if self.__current_group["version"] == 0 else 0
                chars = chr((data >> 8) & 255) + chr(data & 255)
                self.__rt_segments.set_segment(segment + offset, chars)
                terminator = chr(13)
                if terminator in chars:
                    msg = self.__rt_segments.value.replace(terminator, '')
                    self.__set_rt(msg)
        
        except KeyError:
            pass
            

    def __set_pi(self, pi):
        """
        Internal method for setting the PI value,
        observing a changed value and then notifying
        the listener (if provided)
        """
        
        if self.pi != pi:
            self.pi = pi
            if self.__running:
                for listener in self.__listeners:
                    listener.on_pi_change(self, pi)
                

    def __set_ecc(self, ecc):
        """
        Internal method for setting the ECC value,
        observing a changed value and then notifying
        the listener (if provided)
        """
        
        if self.ecc != ecc:
            self.ecc = ecc
            if self.__running:
                for listener in self.__listeners:
                    listener.on_ecc_change(self, ecc)
                

    def __set_ps(self, ps):
        """
        Internal method for setting the PS value,
        observing a changed value and then notifying
        the listener (if provided)
        """
        
        if self.ps != ps:
            self.ps = ps
            if self.__running:
                for listener in self.__listeners:
                    listener.on_ps_change(self, ps)
                

    def __set_rt(self, rt):
        """
        Internal method for setting the RT value,
        observing a changed value and then notifying
        the listener (if provided)
        """
        
        if self.rt != rt:
            self.rt = rt
            if self.__running:
                for listener in self.__listeners:
                    listener.on_rt_change(self, rt)
                