#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import re

from datetime import datetime

FIND_URL = "http://api.geonames.org/searchJSON?q={place}&maxRows=1&username=gcibot"
TIME_URL = "http://api.geonames.org/timezoneJSON?formatted=true&lat={lat}&lng={lng}&username=gcibot&style=full"
WIKIPEDIA_URL = "http://api.geonames.org/wikipediaSearchJSON?formatted=true&q={word}&maxRows=1&username=gcibot&style=full"


def get_date_time(place):
    place_info = requests.get(FIND_URL.format(place=place)).json()
    if not place_info["totalResultsCount"]:
        msg = "~~> %s ~~ city not found" % (lugar)
        return msg

    data = place_info["geonames"][0]
    lat = data["lat"]
    lng = data["lng"]

    timezone_info = requests.get(TIME_URL.format(lat=lat, lng=lng)).json()
    time = datetime.strptime(timezone_info["time"], "%Y-%m-%d %H:%M")
    city = data["name"]
    country = data["countryName"]
    both = "%s, %s" % (city, country)

    if city == country:
        both = country

    msg = "~~> %s ~~ %s ~~ %s" % (both, time.strftime(
        "%H:%M"), time.strftime("(%d/%m/%y)"))
    return msg


def city(city):
    wikipedia_result = requests.get(WIKIPEDIA_URL.format(word=city)).json()
    if not len(wikipedia_result["geonames"]):
        msg = "~~> %s ~~ city not found" % (city)
        return msg
    result = wikipedia_result["geonames"][0]
    result = "~~> %s ~~> %s -- http://%s" % (
        result["title"], result["summary"], result["wikipediaUrl"])
    return result
