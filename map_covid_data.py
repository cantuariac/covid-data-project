
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader

import json
import random
from datetime import date
import math
import argparse

epicenterLine = None
epicenterPoint = None
finalDate = None


def rcolor():
    return (random.random(), random.random(), random.random())

def fcolor2Hex(tcolour):
    return '#%02x%02x%02x'%(int(tcolour[0]*255), int(tcolour[1]*255), int(tcolour[2]*255))

def clamp(value, minv=0, maxv=1): 
    return max(min(value, maxv), minv)

def calculateTotals(countries):
    for country in countries.values():
        if country['data']:
            totalActiveData = {day:0 for day in country['data']}
            break
    
    for day in totalActiveData:
        total = 0
        for country in countries.values():
            if country['data']:
                total += country['data'][day]
        totalActiveData[day] = total
    
    global finalDate
    finalDate = date.fromisoformat(day)
    
    return totalActiveData

def calculateEpicenter(day):
    pass

def plotFrame(day): #, totalActiveData, countriesData, countriesRecords, countriesFeatures, ax):
    
    # day = datetime.date.fromordinal(DAY0 + frame).isoformat()
    epicenterX, epicenterY, epicenterZ = 0.0, 0.0, 0.0
    lon, lat = 0.0, 0.0
    dayKey = day.isoformat()

    for code in countriesData:
        concentration = 0
        if countriesData[code]['data']:
            if totalActiveData[dayKey]>0:
                concentration = countriesData[code]['data'][dayKey] / totalActiveData[dayKey]
                # color = (1.0, clamp(1.0 - concentration), clamp(1.0 - concentration))#)fcolor2Hex(
                color = colorMap(concentration)
            else:
                color = 'white'
            
        else:
            color = 'gray'
        
        countriesFeatures[code]._kwargs['facecolor'] = color
        # countriesFeatures[code].remove()
        # countriesFeatures[code] = ax.add_geometries([countriesRecords[code].geometry],
                                                # ccrs.PlateCarree(), facecolor=color,
                                                # label = code)
        
        # theta += countriesRecords[code].geometry.centroid.x * concentration
        # phi += countriesRecords[code].geometry.centroid.y * concentration

        lon = math.radians(countriesRecords[code].geometry.centroid.x)
        lat = math.radians(countriesRecords[code].geometry.centroid.y)

        epicenterX += math.cos(lat) * math.cos(lon) * concentration
        epicenterY += math.cos(lat) * math.sin(lon) * concentration
        epicenterZ += math.sin(lat) * concentration
    
    lat = math.degrees(math.asin(epicenterZ))
    lon = math.degrees(math.atan2(epicenterY, epicenterX))

    global epicenterLine
    line = epicenterLine.get_data()
    epicenterLine.remove()
    epicenterLine, = plt.plot(plt.np.append(line[0], lon), plt.np.append(line[1], lat), '--', c='black')

    global epicenterPoint
    if epicenterPoint:
        epicenterPoint.remove()
    epicenterPoint, = plt.plot(lon, lat, markersize=4, marker='o', color='red')
    
    plt.title(day.strftime('Date: %b %d %Y'), fontsize=14, fontweight='bold')
    
    print('\rDate:', day.strftime('%b %d %Y'), end='\t')
    print('Epicenter: (%.2f,%.2f) (%.2f,%.2f,%.2f)'%(lon, lat, epicenterX, epicenterY, epicenterZ), end='')


# DAY0 = datetime.date.fromisoformat('2020-01-15').toordinal()

parser = argparse.ArgumentParser()
parser.add_argument('data_type', choices=['active', 'new', 'death'], default='active', const='active', nargs='?')
parser.add_argument('-s', action='store_true', dest='save')
args = parser.parse_args()

countriesDataFile = 'countries_%s_data.json'%args.data_type

f = open(countriesDataFile)
countriesData = json.load(f)
f.close()
print(len(countriesData), ' countries loaded from', countriesDataFile)

totalActiveData = calculateTotals(countriesData)

countriesRecords = {country.attributes['ADM0_A3'] : country for country in shpreader.Reader(shpreader.natural_earth(resolution='110m', category='cultural', name='admin_0_countries')).records()}

countriesFeatures = {} # cartopy.mpl.feature_artist.FeatureArtist
# cartopy.feature.Feature

# matplotlib.use('qt4agg')
fig = plt.figure(figsize=(12.5, 10))

ax = plt.axes(projection=ccrs.PlateCarree()) # cartopy.mpl.geoaxes.GeoAxes.add_feature
ax.set_global()
ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.BORDERS)
ax.add_feature(cartopy.feature.COASTLINE)
# ax.margins(x=0, y=0)
# ax.add_feature(cartopy.feature.Feature(ccrs.PlateCarree(), 0.0, 0.0, markersize=2, marker='o'))


colorNorm = mpl.colors.Normalize(vmin=0, vmax=100)
colorMap = mpl.cm.get_cmap('afmhot_r')
sm = plt.cm.ScalarMappable(cmap=colorMap, norm=colorNorm)
sm._A=[]
colorbar = plt.colorbar(sm, ax=ax, orientation='horizontal', shrink=0.5)#, fraction=0.046
if args.data_type=='active':
    colorbar.set_label('% of global active cases', fontsize=14)
    fig.suptitle('Active Covid-19 Cases', fontsize=18, fontweight='bold')
elif args.data_type=='new':
    colorbar.set_label('% of global daily new cases', fontsize=14)
    fig.suptitle('Daily new Covid-19 Cases', fontsize=18, fontweight='bold')
plt.tight_layout(pad=0.1)

nCountries = 0
for code in countriesData:
    if countriesData[code]['data']:
        color = 'white'
        nCountries += 1
    else:
        color = 'gray'
    
    countriesFeatures[code] = ax.add_geometries([countriesRecords[code].geometry],
                                                ccrs.PlateCarree(), facecolor=color,
                                                label = code)

epicenterLine, = plt.plot([], [])
# print(epicenter, epicenter.get_data())#, dir(epicenter), type(epicenter))

# print(countriesRecords['BRA'].geometry.centroid.xy)
# plotFrame(date(2020, 3, 16))
# plt.draw()
# plt.waitforbuttonpress(0)

# plotFrame(date(2020, 7, 15))
# plt.draw()
# plt.waitforbuttonpress(0)
# print()
# exit()

if args.data_type=='new':
    startDate = date(2020, 1, 31)
else:
    startDate = date(2020, 1, 22)
# finalDate = 

dates = [date.fromordinal(i) for i in range(startDate.toordinal(), finalDate.toordinal())]

ani = animation.FuncAnimation(  fig, plotFrame, frames=dates,
                                # fargs=(totalActiveData, countriesData, countriesRecords, countriesFeatures, ax),
                                interval=200, blit=False)


if args.save:
    ani.save('active_corona.mp4')
else:
    plt.show()
print()
