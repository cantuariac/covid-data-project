
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
import itertools

epicenterLine = None
epicenterPoint = None
finalDate = None


def calculateTotals(countries):
    for country in countries.values():
        if country['data']:
            totalData = {day:0 for day in country['data']}
            break
    
    for day in totalData:
        total = 0
        for country in countries.values():
            if country['data']:
                total += country['data'][day]
        totalData[day] = total
    
    global finalDate
    finalDate = date.fromisoformat(day)
    
    return totalData

def calculateEpicenter(day):
    pass

def plotFrame(day):                                                         # Function to update plot
    epicenterX, epicenterY, epicenterZ = 0.0, 0.0, 0.0
    lon, lat = 0.0, 0.0
    dayKey = day.isoformat()

    for code in countriesData:
        concentration = 0
        if countriesData[code]['data']:
            if totalData[dayKey]>0:
                concentration = countriesData[code]['data'][dayKey] / totalData[dayKey]
                color = colorMap(concentration)                             # Color is weighted 
            else:
                color = 'white'
            
        else:
            color = 'gray'
        
        countriesFeatures[code]._kwargs['facecolor'] = color

        lon = math.radians(countriesRecords[code].geometry.centroid.x)
        lat = math.radians(countriesRecords[code].geometry.centroid.y)

        epicenterX += math.cos(lat) * math.cos(lon) * concentration         # Epicenter is the weighted average centroid
        epicenterY += math.cos(lat) * math.sin(lon) * concentration         # of all countries 
        epicenterZ += math.sin(lat) * concentration
    
    lat = math.degrees(math.asin(epicenterZ))
    lon = math.degrees(math.atan2(epicenterY, epicenterX))

    global epicenterLine
    line = epicenterLine.get_data()
    epicenterLine.remove()                                                   # Update line
    epicenterLine, = plt.plot(plt.np.append(line[0], lon), plt.np.append(line[1], lat), '--', c='black', linewidth=5, alpha=0.5)

    global epicenterPoint
    if epicenterPoint:
        epicenterPoint.remove()                                              # Update epicenter
    epicenterPoint, = plt.plot(lon, lat, markersize= 10, marker='o', color='red', label='Epicenter')
    
    plt.title(day.strftime('Date: %d %b %Y'), fontsize=20, fontweight='bold')
    # plt.legend(handles=[epicenterPoint], loc='lower right')
    print('\rDate:', day.strftime('%d %b %Y'), end='\t')
    print('Epicenter: (%.2f,%.2f) (%.2f,%.2f,%.2f)'%(lon, lat, epicenterX, epicenterY, epicenterZ), end='')


# main

parser = argparse.ArgumentParser(description='Plots Covid-19 data from json file on a map')                                          # Parsing arguments
parser.add_argument('data_type', choices=['active', 'new'], default='active',
                    const='active', nargs='?', help= 'data type to be mapped')
parser.add_argument('-s', action='store_true', dest='save', help='save animation in file')
args = parser.parse_args()

countriesDataFile = 'countries_%s_data.json'%args.data_type

f = open(countriesDataFile)                                                 # Loading collected Covid data
countriesData = json.load(f)
f.close()
print(len(countriesData), ' countries loaded from', countriesDataFile)

totalData = calculateTotals(countriesData)
                                                                            # Loading countries info (geometry, centroid, etc)
countriesRecords = {country.attributes['ADM0_A3'] : country for country in shpreader.Reader(shpreader.natural_earth(resolution='110m', category='cultural', name='admin_0_countries')).records()}

countriesFeatures = {}                                                      # cartopy.mpl.feature_artist.FeatureArtist

fig = plt.figure(figsize=(13.9, 9.5))

ax = plt.axes(projection=ccrs.PlateCarree())                                # Setting up projection
ax.set_global()
ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.BORDERS)
ax.add_feature(cartopy.feature.COASTLINE)

colorNorm = mpl.colors.Normalize(vmin=0, vmax=100)                          # Setting up colorbar and legend
colorMap = mpl.cm.get_cmap('afmhot_r')
sm = plt.cm.ScalarMappable(cmap=colorMap, norm=colorNorm)
sm._A=[]
colorbar = plt.colorbar(sm, ax=ax, orientation='horizontal', shrink=0.5, pad=0.03)
if args.data_type=='active':
    colorbar.set_label('% of global active cases', fontsize=20)
    fig.suptitle('Active Covid-19 Cases', fontsize=26, fontweight='bold')
elif args.data_type=='new':
    colorbar.set_label('% of global daily new cases', fontsize=20)
    fig.suptitle('Daily new Covid-19 Cases', fontsize=26, fontweight='bold')

epicenterPoint = plt.scatter(0, 0, marker='o', color='red', label='Epicenter', s=100)
patch = mpl.patches.Patch(color='grey', label='Missing data')
plt.legend(handles=[epicenterPoint, patch], loc='lower right',fontsize=20)
# plt.legend()
epicenterPoint.remove()
epicenterPoint = None
plt.tight_layout()

nCountries = 0
for code in countriesData:                                                  # Add country geometries
    if countriesData[code]['data']:
        color = 'white'
        nCountries += 1
    else:
        color = 'gray'
    
    countriesFeatures[code] = ax.add_geometries([countriesRecords[code].geometry],
                                                ccrs.PlateCarree(), facecolor=color,
                                                label = code)

epicenterLine, = plt.plot([], [])

if args.data_type=='new':
    startDate = date(2020, 1, 31)
else:
    startDate = date(2020, 1, 22)
# finalDate = date(2020, 3, 22)
                                                                            # Setting date range
# dates = [date.fromordinal(i) for i in range(startDate.toordinal(), finalDate.toordinal())]
ndays = finalDate.toordinal()-startDate.toordinal()
dates = list(itertools.chain.from_iterable([[date.fromordinal(startDate.toordinal()+ i)]*10 for i in range(ndays)]))


ani = animation.FuncAnimation(  fig, plotFrame, frames=dates,               # Animate map
                                interval=20, blit=False)


if args.save:
    
    if args.data_type=='active':
        t='Active Covid-19 Cases'
    elif args.data_type=='new':
        t='Daily new Covid-19 Cases'
    ani.save('covid_epicenter_%s.mp4'%args.data_type, bitrate=1000,        # Save to file
                metadata=dict(title=t, artist='cantuariac'))
else:
    plt.show()
print()
