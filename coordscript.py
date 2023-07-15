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

amountGen = 1
weight = 3000

shapefile = gpd.read_file("cb_2018_us_nation_5m.shp")
#areas = []
#for i in range(0, 51):
#    areas.append(shapefile.loc[i].NAME)

for r in range(0, amountGen):
    loc = shapefile.loc[0]#.loc[random.randint(0, 51)]
    mpolygon = loc.geometry
    gdf_poly = gpd.GeoDataFrame(index=["myPoly"], geometry=[mpolygon])

    x,y = Random_Points_in_Bounds(mpolygon, 100000)
    df = pd.DataFrame()
    df['points'] = list(zip(x,y))
    df['points'] = df['points'].apply(Point)
    gdf_points = gpd.GeoDataFrame(df, geometry='points')

    Sjoin = gpd.tools.sjoin(gdf_points, gdf_poly, predicate="within", how='left')

    # Keep points in "myPoly"
    pnts_in_poly = gdf_points[Sjoin.index_right=='myPoly']

    pointsToCalcDensity = []
    i = 0
    for point in pnts_in_poly.points:
        if point is None:
            continue
        i+=1
        pointsToCalcDensity.append(point)
        if i == weight:
            break
    #print(str(i))

    fp = r'usa_pd_2020_1km.tif'
    img = rasterio.open(fp)
    #show(img)

    band1 = img.read(1)
    highestPoint = None
    highestVal = 0
    for point in pointsToCalcDensity:
        if point.y > img.height or point.x > img.height:
            continue
        #if loc.NAME == 'Puerto Rico':
        if point.x > -70 and point.y < 20 or point.x < -165 and point.y < -10:
            val = 1
        else:
            #print(str(point.x) + ' ' + str(point.y))
            val = band1[img.index(point.x, point.y)]
            
        if (val > highestVal):
            highestVal = val
            highestPoint = point

    print(str(point.y) + " " + str(point.x) + ' -- ' + 'Location ' + str(r))


#base = gdf_poly.boundary.plot(linewidth=1, edgecolor="black")
#pnts_in_poly.plot(ax=base, linewidth=1, color="red", markersize=8)
#plt.show()

#print(band1[img.index(-73.913600, 40.656941)]) # high
#print(band1[img.index(-82.222010, 40.236819)]) # low
