import csv

info={'Longitude': [], 'Latitude': [], 'Callsign':[]}

with open('fm_stations.csv') as fobj:
    next(fobj)
    for line in fobj:
        rawdata = line.split(',')
        info['Longitude'].append(rawdata[0])
        info['Latitude'].append(rawdata[1])
        info['Callsign'].append(rawdata[2].split('-',1)[0])

#print('Longitude:',str(info['Longitude']))
#print('Latitude:',str(info['Latitude'])+'\n')
#print('Callsign:', str(info['Callsign']))
while True: continue

