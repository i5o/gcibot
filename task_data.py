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
from logged_data import GoogleSession

organizations = {
    6541403171586048: "Apertium",
    5154791065911296: "BRL-CAD",
    5731053304020992: "CCExtractor Development",
    5135243763777536: "Catrobat",
    4854733644759040: "CloudCV",
    5636094664114176: "Drupal",
    6237166344601600: "FOSSASIA",
    6281461650948096: "Haiku",
    5733899491606528: "JBoss Community",
    5165875202097152: "LibreHealth",
    5067404587565056: "Liquid Galaxy project",
    5936087526539264: "MetaBrainz Foundation",
    5693523175145472: "MovingBlocks",
    5139786496999424: "OSGeo",
    5753409548320768: "OpenMRS",
    5693741010518016: "OpenWISP",
    4879181169033216: "Sugar Labs",
    4923880235859968: "Sustainable Computing Research Group (SCoRe)",
    5735606506225664: "Systers Community",
    6239808655458304: "The Mifos Initiative",
    5133577048031232: "Ubuntu",
    5740205476675584: "Wikimedia",
    6299430183501824: "XWiki",
    5744567921934336: "Zulip",
    4884530416582656: "coala"
}

api_link = "https://codein.withgoogle.com/api/program/2016/taskdefinition/{taskid}/"
priv_link = "https://codein.withgoogle.com/dashboard/task-instances/{taskid}/"
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
        self.google_session = GoogleSession()

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
                try:
                    task_link = self.google_session.get_public_link(
                        priv_link.format(taskid=task[1]))
                    ids = re.findall(regex_tasks_1, task_link)
                    task = [0, ids[0]]
                except BaseException:
                    self.client.describe(
                        channel, "can't do anything about that link.")
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
