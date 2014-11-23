#! /usr/bin/env python

from v4l2radio import *
import sys
import signal
import time


_DEFAULT_FREQUENCY = 107.8
_RDNS_LOCALE = 'gb'


def main():
    
    try:
        tuner = FMRadio()
    except FMRadioUnavailableError:
        print "FM radio device is unavailable"
        sys.exit(1)
    
    # register signal handler for exiting
    def handler(signum, frame):
        tuner.close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handler)
    
    # tune to a radio service
    frequency = float(sys.argv[1]) if len(sys.argv) is 2 else _DEFAULT_FREQUENCY
    print "Tuning to %0.2f Mhz" % frequency
    
    tuner.set_frequency(frequency * 1000.0)
    tuner.rds.add_listener(RadioDNSRDSListener(_RDNS_LOCALE))
    
    # keep the app running
    while 1:
        time.sleep(1000)
        

if __name__ == "__main__":
    main()
