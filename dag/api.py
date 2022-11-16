from fastapi import FastAPI, Response
from datetime import datetime
from flask import request
import datetime
from urllib.request import urlopen
from PIL import Image,ImageDraw, ImageFont
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import io
from starlette.responses import StreamingResponse
import xarray as xr
import httplib2
import json
import subprocess

def flatten(l):
    out = []
    for i in l:
        for j in i:
            out.append(j)
    return out

def getValueFromColor(pixel_color,color_entry_dict):
    try:
        val = color_entry_dict[tuple(pixel_color)]
    except KeyError:
        val = None
    return val



app = FastAPI()
def datetime_range(date:str, date1:str, steps:int = 1):
    date = date.replace('T00:00:00Z','')
    date1 = date1.replace('T00:00:00Z','')
    t0 = date.split('-')
    t0 = datetime.datetime(int(t0[0]),int(t0[1]),int(t0[2]))
    t1 = date1.split('-')
    t1 = datetime.datetime(int(t1[0]),int(t1[1]),int(t1[2]))
    dif = (t1-t0).days
    inc = dif // steps
    if steps == -1: 
        steps = dif
        inc = 1
    
    out = [str(t0.date()) +'T00:00:00Z' ]
    day = t0
    for i in range(steps):
        day +=datetime.timedelta(days=inc)
        out.append(str(day.date()) + 'T00:00:00Z')
    return out


def gibs(timestamp, scale, layer, colormap, bbox, bins):


    bins = int(bins)
    timestamp = timestamp.replace('-T','T')  # Addreessing timestamp formatting issue
    ormat_='json'
    resolution = 2

    map_height=180*resolution
    map_width=360*resolution
    wms_url = f'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX='+str(bbox)+'CRS=EPSG:4326&WIDTH='+str(map_width)+'&HEIGHT='+str(map_height)+f'&LAYERS={layer}&STYLES=&FORMAT=image/png&TIME='+timestamp
    img_bytes = urlopen(wms_url).read()
    im = Image.open(requests.get(wms_url, stream=True).raw)

    data = np.array(im)

    ###colormap_url = 'https://gibs.earthdata.nasa.gov/colormaps/v1.3/MODIS_Sea_Ice_Daily.xml'
    colormap_url= f'https://gibs.earthdata.nasa.gov/colormaps/v1.3/{colormap.replace(".xml","")}.xml'


    colormap_document = requests.get(colormap_url)
    colormap_document_soup= BeautifulSoup(colormap_document.content,"lxml-xml")

    colormap_entries = colormap_document_soup.find_all("ColorMapEntry",{"value": True})
    color_entry_dict={}
    for row in colormap_entries:
        color_entry={tuple(map(int, (row.attrs['rgb']+',255').split(","))):float(row.attrs['value'][1:-1].split(',')[0].replace("INF", "0"))}
        color_entry_dict.update(color_entry)

    pixels = np.asarray(im)
    raw =[]
    flat = []
    for i in range(im.size[0]): # for every pixel:
        for j in range(im.size[1]):
            flat.append(tuple(list(pixels[j-1,i-1])))
  
    
    for i in flat:
        try:
            raw.append(color_entry_dict[i])
        except:
            pass
    mean_value = np.mean(raw)
    min_value = 0
    max_value = np.max(raw)
    hist = np.histogram(raw, bins=bins)
    stdev_value = np.std(raw)
    median_value = np.median(raw)
    stats = {}
    stats["median"] = str(median_value)

    stats["mean"] = mean_value
    stats["max"] = max_value
    stats["min"] = min_value
    stats["stdev"] =  stdev_value
    stats["hist"] = [[str(j), str(i)] for i, j in zip(hist[0], hist[1])]
    stats["raw"] = list(raw)



    return stats






# CYGNSS_L3_CDR_V1.1
# GHRSST_L4_MUR_Sea_Surface_Temperature
# GHRSST_L4_MUR25_Sea_Ice_Concentration
# http://ec2-3-65-18-201.eu-central-1.compute.amazonaws.com:8080/get_stats?minx=-160&miny=-5&maxx=-150&maxy=0&timestamp=2016-06-09T00:00:00Z&format=json
@app.get("/get_stats", tags=["Home"])
def get_stats(timestamp:str, end_timestamp:str = None, _type:str = 'date',steps: int = 1, layer='GHRSST_L4_MUR_Sea_Surface_Temperature', colormap = 'GHRSST_Sea_Surface_Temperature.xml', _scale=1, bbox:str='-90,-180,90,180', bins:int=10):
    


    if _type == 'range':
        try:
            days = datetime_range(timestamp, end_timestamp, int(str(steps).replace(',','')))
        except Exception as err:
            return f"Invalid time range {err}"
        re = {}
        for day in days:
            re[day] = gibs(str(day), str(_scale), str(layer), str(colormap), str(bbox).replace(' ', ''), int(bins))

        stats = {}
        raws = [ re[i]['raw'] for i in days] 
        raw = flatten(raws)

        mean_value = np.mean(raw)
        min_value = np.min(raw)
        max_value = np.max(raw)
        stdev_value = np.std(raw)
        median_value = np.median(raw)
        hist = np.histogram(raw, bins=int(bins))
        stats["mean"] = mean_value
        stats["median"] = median_value


        stats["max"] = max_value
        stats["min"] = min_value
        stats["stdev"] = stdev_value
        stats["stderr"] = str(np.std(raw) / np.sqrt(len(raw)))
        stats["hist"] = [[str(j), str(i)] for i, j in zip(hist[0], hist[1])]
        stats["raw"] = list(raw)
        return stats     
    if _type == 'series':
        try:
            days = datetime_range(timestamp, end_timestamp, int(str(steps).replace(',','')))
        except Exception as err:
            return f"Invalid time range {err}"
        re = {}
        for day in days:
            re[day] = gibs(str(day), str(_scale), str(layer), str(colormap), str(bbox).replace(' ', ''), int(bins))

        stats = {}
        raws = [ re[i]['raw'] for i in days] 
        raw = flatten(raws)
        median_value = {i:re[i]['median'] for i in days}
        mean_value = {i:re[i]['mean'] for i in days}
        min_value = {i:re[i]['min'] for i in days}
        max_value = {i:re[i]['max'] for i in days}
        stdev_value = {i:re[i]['stdev'] for i in days}
        hist = np.histogram(raw, bins=int(bins))
        stats["mean"] = mean_value
        stats["median"] = median_value
        stats["max"] = max_value
        stats["min"] = min_value
        stats["stdev"] = stdev_value
        stats["stderr"] = str(np.std(raw) / np.sqrt(len(raw)))
        stats["hist"] = [[str(j), str(i)] for i, j in zip(hist[0], hist[1])]
        stats["raw"] = list(raw)
        return stats 

    return gibs(str(timestamp), str(_scale), str(layer), str(colormap), str(bbox).replace(' ', ''), int(bins))

    

  






