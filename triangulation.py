from pyhull.delaunay import DelaunayTri

def getVoronaiPoints(stations):
	coordinates = []
	for station in stations:
		coordinates.append(stations['Coordinates'])

	delaunaryPlanes = DelaunayTri(coordinates)

	print(delaunaryPlanes.vertices)

if __name__ == '__main__':
	stationList = []
	stationList.append({'Callsign': 'WMBI', 'Coordinates': [41.92806, -88.0069]})
	stationList.append({'Callsign': 'WZRD', 'Coordinates': [41.98222, -87.4198]})
	stationList.append({'Callsign': 'WXAV', 'Coordinates': [41.71028, -87.7150]})

	getVoronaiPoints(stations)

	while True: continue