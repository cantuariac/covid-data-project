#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-

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


def getCountries(countries):

    html = requests.get(COVID_URL).text
    soup = BeautifulSoup(html, 'html.parser')
    countryLinks = soup.find(id='main_table_countries_today').select('a.mt_a')

    shpfilename = shpreader.natural_earth(
        resolution='110m', category='cultural', name='admin_0_countries')
    countryRecords = shpreader.Reader(shpfilename).records()
    
    #countries = {}
    mi=0

    for country in countryRecords:
        code = country.attributes['ADM0_A3']
        if code not in countries:
            countries[code]={'code' : code}

        name = country.attributes['NAME_LONG']
        name_short = country.attributes['NAME']
        centroid = (country.geometry.centroid.x, country.geometry.centroid.y)

        search = list(filter(lambda link: link.text==name or link.text==name_short or link.text==code, countryLinks))
        if search:
            path = search[0].attrs['href']
            countryLinks.remove(search[0])
        else:
            path = None
            mi+=1

        if 'name' not in countries[code]: countries[code]['name'] = name
        if 'path' not in countries[code]: countries[code]['path'] = path
        # if 'centroid' not in countries[code]: countries[code]['centroid'] = centroid

    return dict(sorted(countries.items(), key=lambda item: item[1]['name'])), [[link.text, link.attrs['href']] for link in countryLinks]

def main():
    """
    docstring
    """

    f = open('countries_list.json')
    countries = json.load(f)
    f.close()

    print("Collecting list of countries...")
    countries, unmatched = getCountries(countries)
    
    f = open('countries_list.json', 'w')    # os.path.dirname(__file__)
    json.dump(countries, f, indent=2)
    f.close()
    print("List of %d countries collected." % (len(countries)))
    print('Saved on \'countries_list.json\'')

    f = open('unmatched.json', 'w')
    json.dump(unmatched, f, indent=2)
    f.close()
    print (len(unmatched), 'links unmatched')
    print('Saved on \'unmatched.json\'')

if __name__ == '__main__':
    main()
