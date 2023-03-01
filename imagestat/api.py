"""
Defines a FastAPI application and implements the get_stats endpoint
"""
import logging
import re
import datetime

import numpy as np
import requests
from PIL import Image
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException

app = FastAPI()
LOGGER = logging.getLogger('imagestat')


def flatten(list_to_flatten):
    """
    Flattens a list

    :param list_to_flatten:
    :return:
    """
    out = []
    for i in list_to_flatten:
        for j in i:
            out.append(j)
    return out


def get_value_from_color(pixel_color, color_entry_dict):
    """
    Looks up a value using a color

    :param pixel_color:
    :param color_entry_dict:
    :return:
    """
    try:
        val = color_entry_dict[tuple(pixel_color)]
    except KeyError:
        val = None
    return val


def datetime_range(date: str, date1: str, steps: int = 1):
    """
    Produces a list of datetimes at evenly spaced increments between date and date1

    :param date:
    :param date1:
    :param steps:
    :return:
    """
    date = date.replace('T00:00:00Z', '')
    date1 = date1.replace('T00:00:00Z', '')
    time0 = date.split('-')
    time0 = datetime.datetime(int(time0[0]), int(time0[1]), int(time0[2]))
    time1 = date1.split('-')
    time1 = datetime.datetime(int(time1[0]), int(time1[1]), int(time1[2]))
    dif = (time1 - time0).days
    inc = dif // steps
    if steps == -1:
        steps = dif
        inc = 1

    out = [str(time0.date()) + 'T00:00:00Z']
    day = time0
    for _ in range(steps):
        day += datetime.timedelta(days=inc)
        out.append(str(day.date()) + 'T00:00:00Z')
    return out


def gibs(timestamp, layer, colormap, bbox, bins):  # pylint: disable=too-many-locals
    """
    Generate stats for a layer at a particular timestamp

    :param timestamp:
    :param layer:
    :param colormap:
    :param bbox:
    :param bins:
    :return:
    """
    bins = int(bins)
    timestamp = timestamp.replace('-T', 'T')  # Addressing timestamp formatting issue
    resolution = 2

    map_height = 180 * resolution
    map_width = 360 * resolution
    wms_url = f'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap' \
              f'&BBOX={bbox}CRS=EPSG:4326&WIDTH={map_width}&HEIGHT={map_height}&LAYERS={layer}' \
              f'&STYLES=&FORMAT=image/png&TIME={timestamp}'
    image = Image.open(requests.get(wms_url, stream=True, timeout=500).raw)

    colormap_url = f'https://gibs.earthdata.nasa.gov/colormaps/v1.3/{colormap.replace(".xml", "")}.xml'

    colormap_document = requests.get(colormap_url, timeout=500)
    colormap_document_soup = BeautifulSoup(colormap_document.content, features="xml")

    colormap_entries = colormap_document_soup.find_all(re.compile("ColorMapEntry", re.IGNORECASE), {"value": True})
    color_entry_dict = {}
    for row in colormap_entries:
        color_entry = {tuple(map(int, (row.attrs['rgb'] + ',255').split(","))): float(
            row.attrs['value'][1:-1].split(',')[0].replace("INF", "0"))}
        color_entry_dict.update(color_entry)

    pixels = np.asarray(image)
    raw = []
    flat = []
    for i in range(image.size[0]):  # for every pixel:
        for j in range(image.size[1]):
            flat.append(tuple(list(pixels[j - 1, i - 1])))

    for i in flat:
        try:
            raw.append(color_entry_dict[i])
        except KeyError:
            pass
    if raw:
        mean_value = np.mean(raw)
        min_value = 0
        max_value = np.max(raw)
        hist = np.histogram(raw, bins=bins)
        stdev_value = np.std(raw)
        median_value = np.median(raw)
        stats = {"median": str(median_value), "mean": mean_value, "max": max_value, "min": min_value, "stdev": stdev_value,
                 "hist": [[str(j), str(i)] for i, j in zip(hist[0], hist[1])], "raw": list(raw)}
    else:
        stats = {"median": 0, "mean": 0, "max": 0, "min": 0,
                 "stdev": 0,
                 "hist": [[str(j), str(i)] for i, j in zip([0], [0])], "raw": list()}

    return stats


@app.get("/get_stats", tags=["Home"])
# pylint: disable-next=too-many-arguments,too-many-locals
def get_stats(timestamp: str, end_timestamp: str = None, _type: str = 'date', steps: int = 1,
              layer='GHRSST_L4_MUR_Sea_Surface_Temperature', colormap='GHRSST_Sea_Surface_Temperature.xml', _scale=1,
              bbox: str = '-90,-180,90,180', bins: int = 10):
    """
    API endpoint for generating stats for a GIBS layer

    :param timestamp:
    :param end_timestamp:
    :param _type:
    :param steps:
    :param layer:
    :param colormap:
    :param _scale:
    :param bbox:
    :param bins:
    :return:
    """
    if _type == 'range':
        try:
            days = datetime_range(timestamp, end_timestamp, int(str(steps).replace(',', '')))
        except ValueError as err:
            LOGGER.warning("Invalid time range", err)
            raise HTTPException(status_code=400, detail=f"Invalid time range : {err}")
        results = {}
        for day in days:
            results[day] = gibs(str(day), str(layer), str(colormap), str(bbox).replace(' ', ''), int(bins))

        stats = {}
        raws = [results[i]['raw'] for i in days]
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
            days = datetime_range(timestamp, end_timestamp, int(str(steps).replace(',', '')))
        except ValueError as err:
            LOGGER.warning("Invalid time range", err)
            raise HTTPException(status_code=400, detail=f"Invalid time range : {err}")
        results = {}
        for day in days:
            results[day] = gibs(str(day), str(layer), str(colormap), str(bbox).replace(' ', ''), int(bins))

        stats = {}
        raws = [results[i]['raw'] for i in days]
        raw = flatten(raws)
        median_value = {i: results[i]['median'] for i in days}
        mean_value = {i: results[i]['mean'] for i in days}
        min_value = {i: results[i]['min'] for i in days}
        max_value = {i: results[i]['max'] for i in days}
        stdev_value = {i: results[i]['stdev'] for i in days}
        # hist = np.histogram(raw, bins=int(bins))
        stats["mean"] = mean_value
        stats["median"] = median_value
        stats["max"] = max_value
        stats["min"] = min_value
        stats["stdev"] = stdev_value
        stats["stderr"] = str(np.std(raw) / np.sqrt(len(raw)))
        # stats["hist"] = [[str(j), str(i)] for i, j in zip(hist[0], hist[1])]
        # stats["raw"] = list(raw)
        return stats

    return gibs(str(timestamp), str(layer), str(colormap), str(bbox).replace(' ', ''), int(bins))


@app.get("/health", tags=["Health"])
def health_check():
    """
    Allows to check if the API is available

    :return:
    """
    return {
        "status": "ok"
    }
