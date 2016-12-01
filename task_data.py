#!/usr/bin/env python
# -*- coding: utf-8 -*-
# GCI bot. Task data
# Returns data about a task ;)
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

import re
import requests
import json

organizations = {
    5382353857806336: "Apertium",
    4814441002565632: "BRL-CAD",
    6426002725011456: "CCExtractor Development",
    4809822100783104: "Copyleft Games",
    5129917289201664: "Drupal",
    6707477701722112: "FOSSASIA",
    5761416665497600: "Haiku Inc",
    5186916471275520: "KDE",
    4794680462016512: "MetaBrainz Foundation",
    5084291717398528: "Mifos Initiative",
    5452182442737664: "MovingBlocks",
    5747383933599744: "OpenMRS",
    5114486142795776: "Sugar Labs",
    5770017069072384: "Sustainable Computing Research Group ( SCoRe )",
    6025234696110080: "Systers, an Anita Borg Institute Community",
    5385807011512320: "Wikimedia",
    4718815233441792: "Zulip"
}

api_link = "https://codein.withgoogle.com/api/program/2016/taskdefinition/{taskid}/"
regex_tasks_1 = re.compile(
    ur'https{0,1}:\/\/codein\.withgoogle\.com\/tasks\/([0-9]+)\/{0,1}')
regex_tasks_2 = re.compile(
    ur'https{0,1}:\/\/codein\.withgoogle\.com\/dashboard\/task-instances\/([0-9]+)\/{0,1}')
regex_tasks_3 = re.compile(
    ur'https{0,1}:\/\/codein\.withgoogle\.com\/dashboard\/tasks\/([0-9]+)\/{0,1}')
redirect = 'https://codein.withgoogle.com/tasks-instances/{taskid}/'


class TaskFinder():

    def __init__(self, client):
        self.client = client

    def process_msg(self, msg, channel, user):
        msg_tasks = []
        tasks_id = []
        tasks_id_1 = re.findall(regex_tasks_1, msg)
        tasks_id_2 = re.findall(regex_tasks_2, msg)
        tasks_id_3 = re.findall(regex_tasks_3, msg)

        pos = 0
        for tasks in [tasks_id_1, tasks_id_2, tasks_id_3]:
            for task_id in tasks:
                tasks_id.append([pos, task_id])
            pos += 1

        for task in tasks_id:
            if task[0] == 1:
                self.client.describe(channel, "link not supported")
                return []

            json_ = requests.get(api_link.format(taskid=task[1]))
            json_task = json.loads(json_.text)

            msg = "{title} || {days} || {categories} || {org} {whatever}"
            int_days = json_task["time_to_complete_in_days"]

            cat_txt = {1: "Code",
                       2: "User Interface",
                       3: "Documentation",
                       4: "QA",
                       5: "Outreach / Research"}

            categories = ""
            for cat in json_task["categories"]:
                categories += ", " + cat_txt[cat]

            categories = categories[2:]

            whatever = ""

            if json_task["is_beginner"]:
                whatever += "|| Beginner task"

            d = msg.format(
                title=json_task['name'],
                days="%d days" %
                int_days,
                categories=categories,
                org=organizations[json_task["organization_id"]],
                whatever=whatever)

            msg_tasks.append(d)

        return msg_tasks
