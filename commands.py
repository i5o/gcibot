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

public_commands = [
    "ping",
    "about",
    "rules",
    "guide",
    "faq",
    "timeline",
    "!floss",
    "!license",
    "help",
    "memo"]

commands = ["commands", "ping", "about", "rules", "guide", "faq",
            "timeline", "leave this channel", "join",
            "no longer ignore", "ignore", "!license", "ignoring",
            "add admin", "remove admin", "admins", "bored", "!floss",
            "!sugar", "i love you", "coffee", "help", "memo"]

no_interaction_required = ["!license", "!floss", "!sugar"]

about_data = "I'm a bot written by Ignacio, paste GCI link task and \
I will tell data about it.\nSource code available in: https://github.com/i5o/gcibot"

links = {
    "rules": "https://developers.google.com/open-source/gci/resources/contest-rules",
    "guide": "https://developers.google.com/open-source/gci/resources/getting-started",
    "faq": "https://developers.google.com/open-source/gci/faq",
    "timeline": "https://developers.google.com/open-source/gci/timeline",
    "floss": "https://www.gnu.org/philosophy/free-sw.html"}

top_admin = "@unaffiliated/ignacio"
admins = ["@unaffiliated/ignacio"]

licensing_info = "please read: http://people.sugarlabs.org/ignacio/about_licensing.txt"


class Commands():

    def __init__(self, client):
        self.client = client
        self.msg = None
        self.channel = None
        self.user = None
        self.human_user = None
        self.ignored_users = ["meeting"]

        self.pending_msgs = []

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

        for c in commands:
            if c in msg.lower() and not done:
                command = c.replace(" ", "_").replace("!", "")
                output = eval("self.%s()" % command)
                done = True

        if output is not None:
            self.client.msg(channel, output)
            return False

        return True

    def help(self):
        return self.about() + "\nTry 'gcibot, commands' for more commands."

    def i_love_you(self):
        return "%s, I love you too 💕" % self.human_user

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

    def license(self):
        finder = re.compile(ur'!license ([\S*]+)')
        users = finder.findall(self.msg)
        for user in users:
            self.client.msg(self.channel, "%s, %s" % (user, licensing_info))

    def floss(self):
        finder = re.compile(ur'!floss ([\S*]+)')
        users = finder.findall(self.msg.lower())
        for user in users:
            self.client.msg(
                self.channel, "%s, please read: %s" %
                (user, links["floss"]))

    def sugar(self):
        self.client.msg(
            self.channel,
            "Chemical compounds of sugar | glucose (C_6 H_12 O_6) and sucrose (C_12 H_22 O_11) | See: https://en.wikipedia.org/wiki/Sugar")

    def coffee(self):
        self.client.msg(
            self.channel,
            "%s, here is your coffee ☕" %
            self.human_user)

    def commands(self):
        self.client.msg(
            self.channel, "%s, %s" %
            (self.human_user, ", ".join(public_commands)))

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

    def remove_admin(self):
        if not self.is_admin():
            return

        finder = re.compile(ur'([\S*]+)')
        users = finder.findall(self.msg)
        users[0] = None
        users[1] = None
        users[2] = None
        for user in users:
            if user is None or user not in admins or top_admin in user.lower():
                continue

            admins.remove(user)
            self.client.describe(self.channel, "no longer loves %s" %
                                 user)

    def add_admin(self):
        if not self.is_admin():
            return

        finder = re.compile(ur'([\S*]+)')
        users = finder.findall(self.msg)
        users[0] = None
        users[1] = None
        users[2] = None
        for user in users:
            if user is None or user in admins:
                continue

            admins.append(user)
            self.client.describe(self.channel, "loves %s" %
                                 user)

    def admins(self):
        if not self.is_admin():
            return

        str_admins = str(admins)
        self.client.describe(self.channel, "loves %s" % str_admins)

    def memo(self):
        finder = re.compile(ur'([\S*]+)')
        users = finder.findall(self.msg)

        users[0] = None
        users[1] = None
        to = users[2]
        message = " ".join(users[3:len(users)])

        self.pending_msgs.append([self.channel, to, self.human_user, message])
        self.client.describe(
            self.channel,
            "will now wait for the user to join/rejoin the channel.")
