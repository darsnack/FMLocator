# IcecastMetaRDSListener
# Listener class for RDSDecoder which notifies a local Icecast instance to
# update stream meta data with received RDS params
#
# Copyright (C) 2011 <andy.buckingham _AT_ thisisglobal.com>
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


__all__ = ["RadioDNSRDSListener"]


from RDSDecoder import RDSDecoderListener
import urllib2
import base64

# default settings for Icecast instance
_ICECAST_HOST = "localhost"
_ICECAST_PORT = 8000
_ICECAST_USERNAME = "source"
_ICECAST_PASSWORD = "hackme"
_ICECAST_MOUNT = "/mount"


class IcecastMetaRDSDecoderListener(RDSDecoderListener):
    """
    RDSDecoderListener sub-class for monitoring RDS changes that affect
    meta data values for an Icecast mount carrying the related audio
    """
    
    def __init__(self, radio):
        
        RDSDecoderListener.__init__(self, radio)
        
        self.on_reset(None)
        

    def on_ps_change(self, decoder, ps):
        
        self.__update_meta()
        

    def on_rt_change(self, decoder, rt):
        
        self.__update_meta()
        

    def on_reset(self, decoder):
        
        self.__update_meta()
        

    def __update_meta(self, decoder):
        
        ps = self.__radio.rds.ps
        rt = self.__radio.rds.rt
        
        if ps is not None:
            artist = ps.strip()
        else:
            artist = str(self.__radio.getFrequency())
        if rt is not None:
            title = rt.strip()
            song = " - ".join((artist, title))
        else:
            song = artist 
        
        url = "http://%s:%d/admin/metadata?mount=%s&mode=updinfo&song=%s" % (_ICECAST_HOST,
                                                                             _ICECAST_PORT,
                                                                             _ICECAST_MOUNT,
                                                                             urllib2.quote(song))
        request = urllib2.Request(url)
        
        base64string = base64.encodestring('%s:%s' % (_ICECAST_USERNAME,
                                                      _ICECAST_PASSWORD))
        request.add_header('Authorization', 'Basic %s' % base64string)
        urllib2.urlopen(request)
        
