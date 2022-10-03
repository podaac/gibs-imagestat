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
import sys
import json
minx=float(sys.argv[1])
miny=float(sys.argv[2])
maxx=float(sys.argv[3])
maxy=float(sys.argv[4])

timestamp=sys.argv[5]

format_='json'
layer=sys.argv[7]

colormap=sys.argv[8]

scale = float(sys.argv[6])

timestamp = timestamp.replace('-T','T')  # Addreessing timestamp formatting issue

resolution = 2

map_height=180*resolution
map_width=360*resolution

wms_url = f'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX=-90,-180,90,180&CRS=EPSG:4326&WIDTH='+str(map_width)+'&HEIGHT='+str(map_height)+f'&LAYERS={layer}&STYLES=&FORMAT=image/png&TIME='+timestamp
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
out = np.zeros((im.size[1], im.size[0]))
for i in range(im.size[0]): # for every pixel:
    for j in range(im.size[1]):
    #out[j-1,i-1] = getValueFromColor(pixels[j,i],color_entry_dict)
        try:
            out[j-1,i-1] = float(color_entry_dict[tuple(pixels[i,j])]) * scale
        except:
            out[j-1,i-1] = None 
out_pandas = pd.DataFrame(out)
minx_grid = int((180 + minx)*resolution)
maxx_grid = int((180 + maxx)*resolution)
miny_grid = int((90-miny)*resolution)
maxy_grid = int((90-maxy)*resolution)

mean_value = np.nanmean(out_pandas[maxy_grid:miny_grid].iloc[:, minx_grid:maxx_grid].values).round(2)
min_value = np.nanmin(out_pandas[maxy_grid:miny_grid].iloc[:, minx_grid:maxx_grid].values).round(2)
max_value = np.nanmax(out_pandas[maxy_grid:miny_grid].iloc[:, minx_grid:maxx_grid].values).round(2)
stdev_value = np.nanstd(out_pandas[maxy_grid:miny_grid].iloc[:, minx_grid:maxx_grid].values).round(2)


msg = {
    "Mean": mean_value,
    "Max": max_value,
    "Min": min_value,
    "StDev": stdev_value
}

stats = {}
stats["mean"] = str(mean_value)
stats["max"] = str(max_value)
stats["min"] = str(min_value)
stats["stdev"] = str(stdev_value)
print(json.dumps(stats))

