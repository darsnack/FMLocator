#! /usr/bin/env python

import time
import signal
import sys
import os
from pyv4l2radio.src.v4l2radio.FMRadio import *
from pyv4l2radio.src.v4l2radio.RDSDecoder import *
from pyv4l2radio.src.v4l2radio.RadioDNSRDSListener import *

_STATION_FREQUENCY =  101.5
_RDNS_LOCALE = 'gb'

def main():
        try:
                tuner = FMRadio()
        except FMRadioUnavailableError:
                print("FM radio device is unavailable")
                sys.exit(1)

        decoder = RDSDecoder(tuner)
    
        # register signal handler for exiting
        def handler(signum, frame):
               tuner.close()
               decoder.close()
               sys.exit(0)
           
        signal.signal(signal.SIGINT, handler)
          
        # tune to a radio service
        frequency = float(sys.argv[1]) if len(sys.argv) is 2 else _DEFAULT_FREQUENCY
        print("Tuning to %0.2f Mhz" % frequency)
            
        tuner.set_frequency(frequency * 1000.0)
        tuner.rds.add_listener(RadioDNSRDSListener(_RDNS_LOCALE))
        decoder.start()
        decoder.add_listener(RadioDNSRDSListener)

        # keep the app running
        while 1:
                time.sleep(1000)
                print(str(tuner.get_signal_strength()))
                print(str(decoder.__current_group))


        

if __name__ == "__main__":
    main()
