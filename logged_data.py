#!/usr/bin/env python
# -*- coding: utf-8 -*-
# GCI bot.
# Logins in Google and returns the data of a link :)
# Copyright (C) Ignacio Rodríguez <ignacio@sugarlabs.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import requests
from bs4 import BeautifulSoup
import data


class GoogleSession:

    def __init__(self):
        self.ses = requests.session()
        login_html = self.ses.get(
            "https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https%3A%2F%2Fappengine.google.com%2F_ah%2Fconflogin%3Fcontinue%3Dhttps%3A%2F%2Fcodein.withgoogle.com%2Fdashboard%2Ftask-instances%2F5055442791170048%2F&ltmpl#identifier")
        soup_login = BeautifulSoup(
            login_html.content, "lxml").find('form').find_all('input')
        my_dict = {}

        for u in soup_login:
            if u.has_attr('value'):
                my_dict[u['name']] = u['value']

        my_dict['Email'] = data.google_username
        my_dict['Passwd'] = data.google_password

        self.ses.post(
            "https://accounts.google.com/ServiceLoginAuth",
            data=my_dict)

    def get(self, URL):
        return self.ses.get(URL).text

    def get_public_link(self, task):
        x = self.ses.get(task)
        return x.url
