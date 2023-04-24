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

shapefile = gpd.read_file("cb_2018_us_state_20m.shp")
#areas = []
#for i in range(0, 51):
#    areas.append(shapefile.loc[i].NAME)

mpolygon = shapefile.loc[random.randint(0, 51)].geometry
gdf_poly = gpd.GeoDataFrame(index=["myPoly"], geometry=[mpolygon])

x,y = Random_Points_in_Bounds(mpolygon, 1000)
df = pd.DataFrame()
df['points'] = list(zip(x,y))
df['points'] = df['points'].apply(Point)
gdf_points = gpd.GeoDataFrame(df, geometry='points')

Sjoin = gpd.tools.sjoin(gdf_points, gdf_poly, predicate="within", how='left')

# Keep points in "myPoly"
pnts_in_poly = gdf_points[Sjoin.index_right=='myPoly']

print(len(pnts_in_poly))
print(pnts_in_poly)
#print(pnts_in_poly.points[0])

lastpoints = pnts_in_poly.points[0:10]
print(lastpoints)

base = gdf_poly.boundary.plot(linewidth=1, edgecolor="black")
pnts_in_poly.plot(ax=base, linewidth=1, color="red", markersize=8)
plt.show()

#Image.MAX_IMAGE_PIXELS = None
#realimage = Image.open('usa_pd_2020_1km.tif')
#realimage.show()
#im = np.array(realimage, dtype=np.uint8)
#print(im[500, 700])

fp = r'usa_pd_2020_1km.tif'
img = rasterio.open(fp)
#show(img)
#print(img.count)
#print(img.bounds)
#print(img.transform)
#print(img.crs)
band1 = img.read(1)
#print(band1[img.index(-73.913600, 40.656941)]) # high
#print(band1[img.index(-82.222010, 40.236819)]) # low
