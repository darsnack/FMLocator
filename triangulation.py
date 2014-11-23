from scipy.spatial import Delaunay
import numpy

def getMidPoint(points):
	p1 = points[0]
	p2 = points[1]

	return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def getCenterPoint(vertices):
	p1 = vertices[0]
	p2 = vertices[1]
	p3 = vertices[2]

	baseMatrix = [[p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], [1, 1, 1]]
	xMatrix = [[p1[0]**2 + p1[1]**2, p2[0]**2 + p2[1]**2, p3[0]**2 + p3[1]**2], [p1[1], p2[1], p3[1]], [1, 1, 1]]
	yMatrix = [[p1[0], p2[0], p3[0]], [p1[0]**2 + p1[1]**2, p2[0]**2 + p2[1]**2, p3[0]**2 + p3[1]**2], [1, 1, 1]]

	h = numpy.linalg.det(xMatrix) / (2 * numpy.linalg.det(baseMatrix))
	k = numpy.linalg.det(yMatrix) / (2 * numpy.linalg.det(baseMatrix))

	return (h, k)

def getVoronaiPoints(stations):
	voronaiPts = []
	coordinates = []
	for station in stations:
		coordinates.append(station['Coordinates'])

	if (len(coordinates) == 1):
		return (coordinates[0][0], coordinates[0][1])
	elif (len(coordinates) == 2):
		return getMidPoint(coordinates)
	else:
		simplices = Delaunay(coordinates).simplices

		for simplice in simplices:
			voronaiPts.append(getCenterPoint([coordinates[simplice[0]], coordinates[simplice[1]], coordinates[simplice[2]]]))

		return (voronaiPts,simplices,coordinates)

def getStrongestPoint(voronaiPoints,simplices,stations):
	sigStrength = []
	avgSigPower = []
	for station in stations:
		sigStrength.append(station['SignalStrength'])

	for simple in simplices:
		avgSigPower.append((sigStrength[simplices[1]] + sigStrength[simplices[2]] + sigStrength[simplices[3]])/3)

	for sigPower in avgSigPower:
		max = 0
		index = 0
		if sigpower > max:
			max = sigpower
			maxIndex = index
		index += 1

	(lat, lng) = voronaiPoints[maxIndex]
	return (lat,lng)


if __name__ == '__main__':
	stationList = []
	stationList.append({'Callsign': 'WMBI', 'Coordinates': [41.92806, -88.0069]})
	stationList.append({'Callsign': 'WZRD', 'Coordinates': [41.98222, -87.4198]})
	stationList.append({'Callsign': 'WXAV', 'Coordinates': [41.71028, -87.7150]})
	stationList.append({'Callsign': 'WDRV', 'Coordinates': [41.89889, -87.6231]})

	voronai = getVoronaiPoints(stationList)

	print(voronai)