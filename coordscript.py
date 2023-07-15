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

def Random_Points_in_Bounds(polygon, number):   
    minx, miny, maxx, maxy = polygon.bounds
    x = np.random.uniform( minx, maxx, number )
    y = np.random.uniform( miny, maxy, number )
    return x, y

amountGen = 5
weight = 3000
printForGoogleMyMaps = True
showPlot = True
generatedPoints = []

shapefile = gpd.read_file("cb_2018_us_nation_5m.shp")

for r in range(0, amountGen):
    loc = shapefile.loc[0]
    mpolygon = loc.geometry
    gdf_poly = gpd.GeoDataFrame(index=["myPoly"], geometry=[mpolygon])

    x,y = Random_Points_in_Bounds(mpolygon, 300000) # arbitrary num that generates a bunch of locs
    df = pd.DataFrame()
    df['points'] = list(zip(x,y))
    df['points'] = df['points'].apply(Point)
    gdf_points = gpd.GeoDataFrame(df, geometry='points')

    Sjoin = gpd.tools.sjoin(gdf_points, gdf_poly, predicate="within", how='left')

    # Keep points in "myPoly"
    pnts_in_poly = gdf_points[Sjoin.index_right=='myPoly']
    #print(type(pnts_in_poly))
    #print(pnts_in_poly.to_json())
    #print(pnts_in_poly.geometry)

    pointsToCalcDensity = []
    i = 0
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
