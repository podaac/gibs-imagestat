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



def getValueFromColor(pixel_color,color_entry_dict):
    try:
        val = color_entry_dict[tuple(pixel_color)]
    except KeyError:
        val = None
    return val



app = FastAPI()


# CYGNSS_L3_CDR_V1.1
# GHRSST_L4_MUR_Sea_Surface_Temperature
# GHRSST_L4_MUR25_Sea_Ice_Concentration
# http://ec2-3-65-18-201.eu-central-1.compute.amazonaws.com:8080/get_stats?minx=-160&miny=-5&maxx=-150&maxy=0&timestamp=2016-06-09T00:00:00Z&format=json
@app.get("/get_stats", tags=["Home"])
def get_stats(minx:float,miny:float,maxx:float,maxy:float,timestamp:str,format:str, layer='GHRSST_L4_MUR_Sea_Surface_Temperature', colormap = 'GHRSST_Sea_Surface_Temperature.xml', _scale=1):
    
    import subprocess
    return  json.loads(subprocess.check_output(['python', 'get_stats.py', str(minx), str(miny), str(maxx), str(maxy), str(timestamp), str(_scale), str(layer), str(colormap)]).decode())
    

  






