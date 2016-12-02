#!/usr/bin/env python
# -*- coding: utf-8 -*-
# GCI bot. Commands module
#
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
import time

commands = ["commands", "ping", "about", "rules", "guide", "faq",
            "timeline", "leave this channel", "join",
            "no longer ignore", "ignore", "!licensing", "ignoring"]

no_interaction_required = ["!licensing"]

about_data = "I'm a bot written by Ignacio, paste GCI link task and \
I will tell data about it.\nSource code available in: https://github.com/i5o/gcibot"

links = {
    "rules": "https://developers.google.com/open-source/gci/resources/contest-rules",
    "guide": "https://developers.google.com/open-source/gci/resources/getting-started",
    "faq": "https://developers.google.com/open-source/gci/faq",
    "timeline": "https://developers.google.com/open-source/gci/timeline"}

admins = ["@unaffiliated/ignacio"]

licensing_info = "Attribution and Licensing\nPlease read: http://people.sugarlabs.org/ignacio/about_licensing.txt"


class Commands():

    def __init__(self, client):
        self.client = client
        self.msg = None
        self.channel = None
        self.user = None
        self.human_user = None
        self.ignored_users = ["meeting"]

    def process_msg(self, msg, channel, user):
        self.msg = msg
        self.channel = channel
        self.user = user
        self.human_user = user.split('!', 1)[0]

        if self.human_user in self.ignored_users:
            return False

        talking_to_me = msg.startswith(self.client.nickname + ":") \
            or msg.startswith(self.client.nickname + ",") \
            or msg.startswith(self.client.nickname + " ")

        if not talking_to_me:
            no_interaction = False
            for command in no_interaction_required:
                if command in msg.lower():
                    no_interaction = True

            if not no_interaction:
                return True
        done = False
        output = None

        commands.append("bored")
        for c in commands:
            if c in msg.lower() and not done:
                command = c.replace(" ", "_").replace("!", "")
                output = eval("self.%s()" % command)
                done = True
        commands.remove("bored")

        if output is not None:
            self.client.msg(channel, output)
            return False

        return True

    def ping(self):
        return "%s, pong" % self.human_user

    def about(self):
        return "%s, %s" % (self.human_user, about_data)

    def rules(self):
        return "%s, %s" % (self.human_user, links["rules"])

    def guide(self):
        return "%s, %s" % (self.human_user, links["guide"])

    def faq(self):
        return "%s, %s" % (self.human_user, links["faq"])

    def timeline(self):
        return "%s, %s" % (self.human_user, links["timeline"])

    def leave_this_channel(self):
        if not self.is_admin():
            return

        self.client.leave(self.channel)

    def join(self):
        if not self.is_admin():
            return

        finder = re.compile(ur'(#[a-z]+)')
        channels = finder.findall(self.msg)

        for channel in channels:
            self.client.join(channel)

    def is_admin(self):
        is_admin = False

        for admin in admins:
            if admin in self.user:
                is_admin = True

        return is_admin

    def ignore(self):
        if not self.is_admin():
            return

        finder = re.compile(ur'([\S*]+)')
        users = finder.findall(self.msg)
        users[0] = None
        users[1] = None
        for user in users:
            if user is None or user in self.ignored_users:
                continue

            self.ignored_users.append(user)
            self.client.describe(self.channel, "is now ignoring %s" % user)

    def no_longer_ignore(self):
        if not self.is_admin():
            return

        finder = re.compile(ur'([\S*]+)')
        users = finder.findall(self.msg)
        users[0] = None
        users[1] = None
        for user in users:
            if user is None or user not in self.ignored_users:
                continue

            self.ignored_users.remove(user)
            self.client.describe(self.channel, "is no longer ignoring %s" %
                                 user)

    def licensing(self):
        finder = re.compile(ur'!licensing ([\S*]+)')
        users = finder.findall(self.msg)
        for user in users:
            self.client.msg(user, licensing_info)
            self.client.msg(self.channel,
                            "%s, please check your private messages." % user)

    def commands(self):
        self.client.msg(
            self.channel, "%s, %s" %
            (self.human_user, ", ".join(commands)))

    def ignoring(self):
        if not self.is_admin():
            return

        str_ignored = str(self.ignored_users)
        self.client.describe(self.channel, "is ignoring %s" % str_ignored)

    def bored(self):
        if not self.is_admin():
            return

        for channel in self.client.channels:
            self.client.describe(channel, "is bored :(")
