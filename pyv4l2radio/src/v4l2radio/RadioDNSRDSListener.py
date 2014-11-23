# RadioDNSRDSListener
# Listener class for RDSDecoder which implements basic RadioDNS functionality
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


__all__ = ["RadioDNSRDSListener"]


from RDSDecoder import RDSDecoderListener
import dns.resolver


class RadioDNSRDSListener(RDSDecoderListener):
    """
    RDSDecoderListener sub-class for monitoring RDS changes that affect
    RadioDNS service resolution
    """
    
    def __init__(self, country = 'gb'):
        
        RDSDecoderListener.__init__(self)
        
        self.__country = country
        self.on_reset(None)
        

    def on_pi_change(self, decoder, pi):
        
        self.__check_radiodns_values(decoder.radio)
        

    def on_ecc_change(self, decoder, ecc):
        
        self.__check_radiodns_values(decoder.radio)
        

    def on_reset(self, decoder):
        
        self.authFqdn = None
        self.apps = {}
        

    def __check_radiodns_values(self, radio):
        
        frequency = str(radio.get_frequency() / 10).zfill(5) 
        pi = radio.rds.pi
        ecc = radio.rds.ecc
        
        if not pi:
            return
        
        if ecc and pi:
            fqdn = "%s.%s.%s.fm.radiodns.org." % (frequency,
                                                 pi[2:],
                                                 pi[2:3] + ecc[2:])
        else:
            fqdn = "%s.%s.%s.fm.radiodns.org." % (frequency,
                                                 pi[2:],
                                                 self.__country)
        
        try:
            answers = dns.resolver.query(fqdn, "CNAME")
            self.authFqdn = str(answers[0])[:-1]
        except:
            return
        
        self.apps = {}
        for app in ("radioepg", "radiotag", "radiovis"):
            appFqdn = "_%s._tcp.%s" % (app, self.authFqdn)
            try:
                answers = dns.resolver.query(appFqdn, "SRV")
            except:
                continue
            self.apps[app] = []
            for answer in answers:
                self.apps[app].append({"target": str(answer.target)[:-1],
                                       "port": int(answer.port),
                                       "priority": int(answer.priority),
                                       "weight": int(answer.weight)})
                
