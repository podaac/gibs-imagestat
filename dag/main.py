from fastapi import FastAPI, Response
from datetime import datetime

from urllib.request import urlopen
from PIL import Image,ImageDraw, ImageFont
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import io
from starlette.responses import StreamingResponse, JSONResponse
import xarray as xr
 



def getValueFromColor(pixel_color,color_entry_dict):
    try:
        val = color_entry_dict[tuple(pixel_color)]
    except KeyError:
        val = None
    return val



app = FastAPI()


@app.get("/", tags=["Health"])
def healthcheck():
    return JSONResponse(content={})


# http://ec2-3-65-18-201.eu-central-1.compute.amazonaws.com:8080/get_stats?minx=-160&miny=-5&maxx=-150&maxy=0&timestamp=2016-06-09T00:00:00Z
@app.get("/get_stats", tags=["Home"])
def get_stats(minx:float,miny:float,maxx:float,maxy:float,timestamp:str):
    resolution = 2

    map_height=180*resolution
    map_width=360*resolution

    wms_url = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX=-90,-180,90,180&CRS=EPSG:4326&WIDTH='+str(map_width)+'&HEIGHT='+str(map_height)+'&LAYERS=GHRSST_L4_MUR_Sea_Surface_Temperature&STYLES=&FORMAT=image/png&TIME='+timestamp
    #img_bytes = urlopen(wms_url).read()
    im = Image.open(requests.get(wms_url, stream=True).raw)

    data = np.array(im)

    print ('fetched xarray data...')

    colormap_url = 'https://gibs.earthdata.nasa.gov/colormaps/v1.3/GHRSST_Sea_Surface_Temperature.xml'
    colormap_document = requests.get(colormap_url)
    colormap_document_soup= BeautifulSoup(colormap_document.content,"lxml-xml")

    colormap_entries = colormap_document_soup.find_all("ColorMapEntry",{"sourceValue": True})
    color_entry_dict={}
    for row in colormap_entries:
        color_entry={tuple(map(int, (row.attrs['rgb']+',255').split(","))):float(row.attrs['sourceValue'][1:-1].split(',')[0].replace("INF", "0"))}
        color_entry_dict.update(color_entry)

    # pixels = im.load() # create the pixel map
    pixels = np.asarray(im)
    out = np.zeros((im.size[1], im.size[0]))
    for i in range(im.size[0]): # for every pixel:
        for j in range(im.size[1]):
            out[j-1,i-1] = getValueFromColor(pixels[j,i],color_entry_dict)
    out_pandas = pd.DataFrame(out)

    minx_grid = int((180 + minx)*resolution)
    maxx_grid = int((180 + maxx)*resolution)
    miny_grid = int((90-miny)*resolution)
    maxy_grid = int((90-maxy)*resolution)

    mean_value = round(np.nanmean(out_pandas[maxy_grid:miny_grid].iloc[:, minx_grid:maxx_grid].values), 2)
    min_value = round(np.nanmin(out_pandas[maxy_grid:miny_grid].iloc[:, minx_grid:maxx_grid].values), 2)
    max_value = round(np.nanmax(out_pandas[maxy_grid:miny_grid].iloc[:, minx_grid:maxx_grid].values), 2)
    stdev_value = round(np.nanstd(out_pandas[maxy_grid:miny_grid].iloc[:, minx_grid:maxx_grid].values), 2)


    msg = {
        "Mean": mean_value,
        "Max": max_value,
        "Min": min_value,
        "StDev": stdev_value
    }

    datem = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    year_day = datem.timetuple().tm_yday 
    ghrsst_resolution=4 # 0.25 degree    
    ghrsst_minx_grid = int((180 + minx)*ghrsst_resolution)
    ghrsst_maxx_grid = int((180 + maxx)*ghrsst_resolution)
    ghrsst_miny_grid = int((90+miny)*ghrsst_resolution)
    ghrsst_maxy_grid = int((90+maxy)*ghrsst_resolution)
    ghrsst_url = 'https://podaac-opendap.jpl.nasa.gov/opendap/hyrax/allData/ghrsst/data/GDS2/L4/GLOB/JPL/MUR25/v4.2/'+str(datem.year)+'/'+str(year_day)+'/'+datem.strftime("%Y%m%d")+'090000-JPL-L4_GHRSST-SSTfnd-MUR25-GLOB-v02.0-fv04.2.nc?time[0:1:0],lat['+str(ghrsst_miny_grid)+':1:'+str(ghrsst_maxy_grid)+'],lon['+str(ghrsst_minx_grid)+':1:'+str(ghrsst_maxx_grid)+'],analysed_sst[0:1:0]['+str(ghrsst_miny_grid)+':1:'+str(ghrsst_maxy_grid)+']['+str(ghrsst_minx_grid)+':1:'+str(ghrsst_maxx_grid)+']'
    ds =xr.open_dataset(ghrsst_url, decode_times=False).to_dataframe()
    ds['sst']=ds['analysed_sst']-273.15  # Convert to Celsius



    msg_ghrsst = {
        "Mean": round(ds['sst'].mean(), 2),
        "Max": round(ds['sst'].max(), 2),
        "Min": round(ds['sst'].min(), 2),
        "StDev": round(ds['sst'].std(), 2)
    }

    




    
    img = Image.new('RGB', (280, 160), color = (0,0,0))
    fnt = ImageFont.truetype('/home/admin/WorldView/Calibri.ttf', 15)
    d = ImageDraw.Draw(img)
    d.text((10,10), "Timestamp: "+timestamp+"\n\nDerived from GIBS:\n  Mean: "+str(mean_value)+"°C\n  Max: "+str(max_value)+"°C\n"+"  Min: "+str(min_value)+"°C\n"+"  StdDev: "+str(round(stdev_value,2))+"°C\n",font=fnt,fill=(218, 247, 166))
    d.text((140,10), "\n\nUnderlying GHRSST:\n  Mean: "+str(msg_ghrsst['Mean'])+"°C\n  Max: "+str(msg_ghrsst['Max'])+"°C\n"+"  Min: "+str(msg_ghrsst['Min'])+"°C\n"+"  StdDev: "+str(msg_ghrsst['StDev'])+"°C\n",font=fnt,fill=(218, 247, 166))
    
    image = io.BytesIO()
    img.save(image, format='PNG') 
    #imsave(image, img, format='PNG', quality=100)
    image.seek(0) 
    #return StreamingResponse(image, media_type="image/png")
    return Response(content=image.getvalue(), media_type="image/png")
    # return StreamingResponse(io.BytesIO(img.tobytes()), media_type="image/png")
    #return StreamingResponse(image.read(), media_type="image/png")



