import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
import pandas as pd
# Plot result
import matplotlib.pyplot as plt
from PIL import Image
import rasterio
from rasterio.plot import show
import random

class Metro:
    def __init__(self, polygon, chance):
        self.polygon = polygon
        self.chance = chance

def Random_Points_in_Bounds(polygon, number):   
    minx, miny, maxx, maxy = polygon.bounds
    x = np.random.uniform( minx, maxx, number )
    y = np.random.uniform( miny, maxy, number )
    return x, y

amountGen = 1 # number of locations generated in this run
weight = 200 # number of locations compared to find the one with highest population density (higher = likely to find higher density locs)
printForGoogleMyMaps = False # True to print in a format that can be imported into Google My Maps if copied into a .csv file; False will just print the coordinate
showPlot = True # True to show a map after generating all locs with all of the points generated shown
reduceTopMetros = False # True to limit the number of locations generated in large metro areas (metro configuration shown below)

generatedPoints = []

# rough approximations for different metro areas
# chance of the end result being this metro area is reduced using the 2nd value at the very end
# example, LA area with 0.15 chance means there's a 15% chance LA locations don't get thrown out
# this is all ignored if reduceTopMetros is false
metros = []
metros.append(Metro(Polygon([(-118.5911, 34.2418), (-117.1217, 34.2418), (-117.1217, 33.6060), (-118.5911, 33.2418)]), 0.25)) ## LA area
metros.append(Metro(Polygon([(-74.325783, 40.884711), (-74.325783, 40.475277), (-73.608120, 40.475277), (-73.608120, 40.884711)]), 0.25)) ## NYC area
metros.append(Metro(Polygon([(42.342692, -88.353000), (42.342692, -87.273094), (41.465876, -87.273094), (41.465876, -88.353000)]), 0.25)) ## chicago area
metros.append(Metro(Polygon([(30.129992, -95.876721), (29.488927, -95.876721), (29.488927, -95.025281), (30.129992, -95.025281)]), 0.25)) ## houston area
metros.append(Metro(Polygon([(-122.631391, 38.048568), (-121.7717, 38.048568), (-121.771710, 37.239558), (-122.6314, 37.2396)]), 0.30)) ## bay area
metros.append(Metro(Polygon([(39.099434, -77.554272), (39.099434, -76.801709), (38.663270, -76.801709), (38.663270, -77.554272)]), 0.25)) ## DC area
metros.append(Metro(Polygon([(33.263100, -97.521924), (32.548268, -97.521924), (32.548268, -96.516675), (33.263100, -96.516675)]), 0.25)) ## DFW area
metros.append(Metro(Polygon([(40.173570, -75.449877), (39.843283, -75.449877), (39.843283, -74.892321), (40.173570, -74.892321)]), 0.30)) ## philly area
metros.append(Metro(Polygon([(48.003486, -122.520270), (47.225873, -122.520270), (48.003486, -122.012152), (47.225873, -122.012152)]), 0.30)) ## seattle area
metros.append(Metro(Polygon([(42.525750, -71.255876), (42.525750, -71.255876), (42.525750, -70.923540), (42.525750, -70.923540)]), 0.30)) ## boston area
metros.append(Metro(Polygon([(39.969730, -105.231390), (39.528384, -105.231390), (39.528384, -104.712286), (39.969730, -104.712286)]), 0.30)) ## denver area
metros.append(Metro(Polygon([(36.314008, -115.357056), (35.981678, -115.357056), (35.981678, -114.923539), (36.314008, -114.923539)]), 0.30)) ## LV area
metros.append(Metro(Polygon([(25.426485, -79.981053), (26.555904, -79.992576), (26.555904, -80.511680), (25.426485, -80.511680)]), 0.25)) ## miami area
metros.append(Metro(Polygon([(32.560054, -117.494406), (33.292011, -117.494406), (33.292011, -116.879172), (32.560054, -116.879172)]), 0.30)) ## san diego area
metros.append(Metro(Polygon([(32.803943, -112.498374), (33.932466, -112.498374), (33.932466, -111.454673), (32.803943, -111.454673)]), 0.30)) ## phoenix area

shapefile = gpd.read_file("cb_2018_us_nation_5m.shp")

if printForGoogleMyMaps:
    print("WKT,name,description")

for r in range(0, amountGen):
    chance = random.random()
    loc = shapefile.loc[0]
    mpolygon = loc.geometry
    gdf_poly = gpd.GeoDataFrame(index=["myPoly"], geometry=[mpolygon])

    x,y = Random_Points_in_Bounds(mpolygon, weight * 500) # this is arbitrarily enough locs to generate where at least (weight) amount will be within US borders
    df = pd.DataFrame()
    df['points'] = list(zip(x,y))
    df['points'] = df['points'].apply(Point)
    gdf_points = gpd.GeoDataFrame(df, geometry='points')

    Sjoin = gpd.tools.sjoin(gdf_points, gdf_poly, predicate="within", how='left')

    # filter points generated to only keep ones within US borders
    pnts_in_poly = gdf_points[Sjoin.index_right=='myPoly']
    #print(type(pnts_in_poly))
    #print(pnts_in_poly.to_json())
    #print(pnts_in_poly.geometry)

    pointsToCalcDensity = []
    i = 0
    #print(pnts_in_poly.count())
    for point in pnts_in_poly.points:
        if point is None:
            continue
        i+=1
        pointsToCalcDensity.append(point)
        if i == weight:
            break

    fp = r'usa_pd_2020_1km.tif'
    img = rasterio.open(fp)
    band1 = img.read(1)
    
    highestPoint = None
    highestVal = 0
    for point in pointsToCalcDensity:
        if point.y > img.height or point.x > img.height:
            continue
        # vague bounds for US states
        # if something is found outside of bounds it is essentially ignored
        if point.x > -70 and point.y < 20 or point.x < -165 and point.y < -10:
            val = 1
        else:
            #print(str(point.x) + ' ' + str(point.y))
            val = band1[img.index(point.x, point.y)]

        # if highest population density found so far, choose it
        if (val > highestVal):
            # this checks if is within one of the metros that we filter from
            # if so, maybe filter
            if reduceTopMetros:
                breakout = False
                for metro in metros:
                    if (chance > metro.chance) and metro.polygon.contains(point):
                        breakout = True
                        break
                if breakout:
                    continue
            # gotten through those filters? set this to the best found location so far
            highestVal = val
            highestPoint = point

    generatedPoints.append(highestPoint)
    if printForGoogleMyMaps:
        print('"' + str(highestPoint) + '",' + 'Location ' + str(r) + ',')
    else:
        print(str(highestPoint.y) + " " + str(highestPoint.x))

if showPlot:
    ndf = pd.DataFrame({ "Points": generatedPoints })
    ngdf = gpd.GeoDataFrame(ndf, geometry=generatedPoints, crs="EPSG:4326")

    base = gdf_poly.boundary.plot(linewidth=1, edgecolor="black")
    ngdf.plot(ax=base, linewidth=1, color="red", markersize=10)

    plt.xlim([-180, -60])
    plt.ylim([15, 75])
    plt.show()
