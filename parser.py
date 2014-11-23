

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
    result=data_parser()
    print('Longitude:',str(result['Longitude']))
    print('Latitude:',str(result['Latitude'])+'\n')
    print('Callsign:',str(result['Callsign']))
    while True: continue

