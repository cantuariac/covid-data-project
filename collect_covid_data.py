
import requests
import json
import os
import argparse
import datetime
import sys

from bs4 import BeautifulSoup
import cartopy.io.shapereader as shpreader


# sys.path.append('./..')
# from useless.loading import ProgressBarThread

COVID_URL = 'https://www.worldometers.info/coronavirus/'

def getCountryData(path, data_type='active'):
    html = requests.get(COVID_URL + path).text
    soup = BeautifulSoup(html, 'html.parser')

    if data_type=='active':
        scriptStr = str(soup.select('#graph-active-cases-total')
                        [0].findNextSibling('script').contents[0])
        start = scriptStr.find('data')
    elif data_type=='new':
        scriptStr = str(soup.select('#graph-cases-daily')
                        [0].findNextSibling('script').contents[0])
        start = scriptStr.find('7-day moving average')
        start = start + scriptStr[start:].find('data')
    
    start = start + scriptStr[start:].find('[')
    end = start + scriptStr[start:].find(']')
    data = json.loads(scriptStr[start:end+1])

    start = scriptStr.find('categories')
    start = start + scriptStr[start:].find('[')
    end = start + scriptStr[start:].find(']')
    dates = json.loads(scriptStr[start:end+1])


    dataByDate = {}

    for i in range(len(dates)):
        dateStr = datetime.datetime.strptime(
            dates[i], '%b %d, %Y').date().isoformat()
        if data[i] == None:
            dataByDate[dateStr] = 0
        else:
            dataByDate[dateStr] = data[i]
    
    missingDate = datetime.date(2020,1,22)
    while (missingDate.isoformat() not in dataByDate):
        dataByDate[missingDate.isoformat()] = 0
        missingDate = missingDate.fromordinal(missingDate.toordinal()+1)

    return dict(sorted(dataByDate.items(), key=lambda item: item[0]))

def main():

    parser = argparse.ArgumentParser(description='Parses Covid-19 data from the web and saves in json file')
    parser.add_argument('data_type', choices=['active', 'new'], default='active', const='active', nargs='?', help='data type to be collected')
    args = parser.parse_args()

    countriesListFile = 'countries_list.json'         #os.path.dirname(__file__)
    countriesDataFile = 'countries_%s_data.json'%args.data_type

    f = open(countriesListFile)
    countriesList = json.load(f)
    f.close()
    print(len(countriesList), ' countries loaded from', countriesListFile)

    if args.data_type == 'active':
        print('Collecting active Covid-19 cases data')
    elif args.data_type == 'new':
        print('Collecting new Covid-19 cases data')

    # progressBar = ProgressBarThread(2, 10)
    # progressBar.start()


    for i, code in enumerate(countriesList):
        # print('(%d/%d) Collecting %s data...' %
        #       (i+1, len(countries), name), end='\r', flush=True)

        try:
            if countriesList[code]['path']:
                dataByOrdinalDate = getCountryData(countriesList[code]['path'], args.data_type)
            else:
                raise Exception('Missing link')
        except Exception as e:
            print(countriesList[code]['name'], 'collection fail:', e.args)
            countriesList[code]['data'] = None
        else:
            countriesList[code]['data'] = dataByOrdinalDate
            # progressBar.print(countriesList[code]['name'], 'data collected.             ')
        
        # progressBar.set_progress((i+1)/len(countriesList))
    
    for code in countriesList:                              # setting Antarctica data to 0
        if countriesList[code]['data']:                   # so it shows as white on the map
            countriesList['ATA']['data'] = {d : 0 for d in countriesList[code]['data']}
            break

    # progressBar.join()
    print('Collection complete!')

    f = open(countriesDataFile, 'w')
    json.dump(countriesList, f, indent=2)
    f.close()


    print('Data saved on', countriesDataFile)

if __name__=='__main__':
    main()