#!/usr/bin/env python
import requests
import re
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dateutil import tz

COORDS_API_URL = "https://maps.googleapis.com/maps/api/geocode/json?language=en_US&address={address}&sensor=false"
TIMEZONE_API_URL = "https://maps.googleapis.com/maps/api/timezone/json?location={coords}&timestamp={timestamp}"


def get_coords(data):
    coords = requests.get(COORDS_API_URL.format(address=data)).json()
    if "ZERO" in coords['status']:
        return ("not found", None, None)

    lat = coords['results'][0]['geometry']['bounds']['northeast']['lat']
    lng = coords['results'][0]['geometry']['bounds']['northeast']['lng']
    return (coords, lat, lng)


def get_time_data(txt_coords):
    timestamp = int(time.time())
    time_url = TIMEZONE_API_URL.format(coords=txt_coords, timestamp=timestamp)
    time_data = requests.get(time_url).json()
    return time_data


def convert_time(to_time_zone):
    from_zone = tz.gettz('UTC+1')
    to_zone = tz.gettz(to_time_zone)
    utc = datetime.utcnow()
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    return (central, to_zone, central.strftime("%H:%M (%d/%m)"))


def get_city_and_country(result):
    try:
        city = result['results'][0]['address_components'][0]['long_name']
        country = result['results'][0]['address_components'][2]['long_name']
        return "%s, %s" % (city, country)
    except IndexError:
        country = result['results'][0]['address_components'][0]['long_name']
        return "%s" % country


def get_time_zone(result):
    return result['timeZoneId']


def get_time(msg, human_user):
    finder = re.compile(ur'([\S*]+)')
    addresses = finder.findall(msg)
    if not addresses[0] == ".time":
        return None

    addresses[0] = ""
    cmd = " ".join(addresses)[1:]

    coords, lat, lng = get_coords(cmd)
    if coords == "not found":
        return "%s, [%s] City not found" % (human_user, cmd)

    txt_coords = "%s,%s" % (lat, lng)
    time_data = get_time_data(txt_coords)
    tt, tz, str_time = convert_time(get_time_zone(time_data))
    str_zone = get_city_and_country(coords)

    return "%s, [%s] %s" % (human_user, str_zone, str_time)


def time_until(city_country, _time, to_zone, day=1, month=1, year=2017):
    rd = relativedelta(_time, datetime(2017, 1, 1, tzinfo=to_zone))

    hours = -(rd.hours)
    minutes = -(rd.minutes)
    seconds = -(rd.seconds)
    msg = "New Year will happen in %s in %d hours, %d minutes, and %d seconds" % (
        city_country, hours, seconds, minutes)
    if hours < 0 or minutes < 0:
        hours = -(hours)
        minutes = -(minutes)
        seconds = -(seconds)
        msg = "New Year already happened in %s, %d hours, %d minutes, and %d seconds ago." % (
            city_country, hours, seconds, minutes)
    return msg
