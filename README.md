# covid-data-project
Python scripts for colectting and visualizing Covid-19 data day by day on a map.

Data source: [Worldometer](https://www.worldometers.info/coronavirus/)

Tools:
- Python
- matplotlib
- cartopy
- ffmpeg

# Exemple

https://github.com/user-attachments/assets/6f1df3f7-fdb8-4523-8d9f-4988c3dbbc6d

# Usage

Run `collect_covid_data.py` to update the data from the web.

```
$ python collect_covid_data.py -h
usage: collect_covid_data.py [-h] [{active,new}]

Parses Covid-19 data from the web and saves in json file

positional arguments:
  {active,new}  data type to be collected

optional arguments:
  -h, --help    show this help message and exit
```

Run `map_covid_data.py` to show or save animation.

```
$ python map_covid_data.py -h
usage: map_covid_data.py [-h] [-s] [{active,new}]

Plots Covid-19 data from json file on a map

positional arguments:
  {active,new}  data type to be mapped

optional arguments:
  -h, --help    show this help message and exit
  -s            save animation in file
```
