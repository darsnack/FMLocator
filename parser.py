from string import ascii_uppercase

def piToCall(piCode):
    piDeci = int(piCode,16)
    callsign = ""
    digits = str(piDeci)
    if piDeci >= 21672:
        callsign+="W"
        inductor = piDeci - 21762
        print(int_to_b26(inductor))
        callsign+=int_to_b26(inductor)

    else:
        callsign+="K"
        inductor = piDeci - 4096
        callsign+=base10toN(int(piCode[1]),26)
        callsign+=base10toN(int(piCode[2]),26)
        callsign+=base10toN(int(piCode[3]),26)
    return callsign

def int_to_b26(n):
    if n < 25:
        return ascii_uppercase[n]
    else:
        q, r = divmod(n, 25)
        return int_to_b26(q) + ascii_uppercase[r]
    

def data_parser():

    info={'Longitude': [], 'Latitude': [], 'Callsign':[]}
    with open('fm_stations.csv') as fobj:
        next(fobj)
        for line in fobj:
            rawdata = line.split(',')
            info['Longitude'].append(rawdata[0])
            info['Latitude'].append(rawdata[1])
            info['Callsign'].append(rawdata[2].split('-',1)[0])
    return info

   
if __name__=="__main__":
    callsign = piToCall("9331")
    print(callsign)
