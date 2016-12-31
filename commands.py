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
import datetime
import data

public_commands = [
    "ping",
    "about",
    "rules",
    "guide",
    "faq",
    "timeline",
    "!floss",
    "!license",
    "thanks",
    "!musicblocks",
    "help",
    "pending memos",
    "memo",
    "hi",
    "ignore me"]

commands = [
    "i rock",
    "you rock",
    "all memos",
    "pending memos",
    "memo",
    "you can stand",
    "allcommands",
    "commands",
    "ping",
    "about",
    "rules",
    "guide",
    "faq",
    "timeline",
    "leave this channel",
    "join",
    "no longer ignore",
    "ignore me",
    "ignore",
    "!license",
    "ignoring",
    "add admin",
    "remove admin",
    "admins",
    "bored",
    "!floss",
    "!sugar",
    "i love you",
    "!coffee",
    "help",
    "!thanks",
    "!musicblocks",
    "!high5",
    "!hi5",
    "thanks",
    "!nick",
    "hi",
    "!hi",
    "!register",
    "!svineet"]

no_interaction_required = [
    "!license",
    "!floss",
    "!sugar",
    "!musicblocks",
    "!coffee",
    "!tea",
    "!thanks",
    "!high5",
    "!hi5",
    "!nick",
    "!register",
    "!svineet"]

about_data = "I'm a bot written by Ignacio, paste GCI link task and \
I will tell data about it.\nSource code available in: https://github.com/i5o/gcibot"

music_blocks = """Music Blocks code is here: https://github.com/walterbender/musicblocks You can try Music Blocks at https://play.musicblocks.net. Also, WE CURRENTLY RECOMMEND FIREFOX, because of a bug with Chrome/ium (currently versions 53+ plays wrong notes)."""

links = {
    "rules": "https://developers.google.com/open-source/gci/resources/contest-rules",
    "guide": "https://developers.google.com/open-source/gci/resources/getting-started",
    "faq": "https://developers.google.com/open-source/gci/faq",
    "timeline": "https://developers.google.com/open-source/gci/timeline",
    "floss": "https://www.gnu.org/philosophy/free-sw.html"}

admins = ["@unaffiliated/ignacio", "@unaffiliated/tymonr"]

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

        if self.human_user in self.ignored_users and not "ignore me" in self.msg:
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

    def hi(self):
        return "Hi %s :)" % self.human_user

    def hi5(self):
        self.high5()

    def high5(self):
        self.client.describe(self.channel, "HIGH FIVES ALL AROUND!!!")

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
            if user is None or user in self.ignored_users or user in admins:
                continue

            self.ignored_users.append(user)
            self.client.describe(self.channel, "is now ignoring %s" % user)

    def ignore_me(self):
        if self.human_user in self.ignored_users:
            self.ignored_users.remove(self.human_user)
            self.client.describe(
                self.channel,
                "is no longer ignoring  %s :)" %
                self.human_user)
        else:
            self.ignored_users.append(self.human_user)
            self.client.describe(
                self.channel,
                "is now ignoring %s :(" %
                self.human_user)

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
        done = False
        for user in users:
            self.client.msg(self.channel, "%s, %s" % (user, licensing_info))

            done = True

        if not done:
            self.client.msg(
                self.channel, "%s, %s" %
                (self.human_user, licensing_info))

    def floss(self):
        finder = re.compile(ur'!floss ([\S*]+)')
        users = finder.findall(self.msg.lower())
        done = False
        for user in users:
            self.client.msg(
                self.channel, "%s, please read: %s" %
                (user, links["floss"]))
            done = True

        if not done:
            self.client.msg(
                self.channel, "%s, please read: %s" %
                (self.human_user, links["floss"]))

    def sugar(self):
        self.client.msg(
            self.channel,
            "Chemical compounds of sugar | glucose (C_6 H_12 O_6) and sucrose (C_12 H_22 O_11) | See: https://en.wikipedia.org/wiki/Sugar")

    def coffee(self, is_tea=False):
        finder = re.compile(ur'!coffee ([\S*]+)')
        users = finder.findall(self.msg.lower())
        done = False
        word = 'coffee'
        if is_tea:
            word = 'tea'
        for user in users:
            self.client.msg(
                self.channel, "%s, here is your %s ☕" % (user, word))
            done = True

        if not done:
            self.client.msg(
                self.channel, "%s, here is your %s ☕" %
                (self.human_user, word))

    def tea(self):
        self.coffee(self, True)

    def thanks(self):
        self.client.msg(
            self.channel,
            "%s, you are quite welcome. :)" %
            self.human_user)

    def musicblocks(self):
        finder = re.compile(ur'!musicblocks ([\S*]+)')
        users = finder.findall(self.msg.lower())
        done = False
        for user in users:
            self.client.msg(
                self.channel, "%s, %s" %
                (user, music_blocks))
            done = True
        if not done:
            self.client.msg(
                self.channel, "%s, %s" %
                (self.human_user, music_blocks))

    def commands(self):
        self.client.msg(
            self.channel, "%s, %s" %
            (self.human_user, ", ".join(public_commands)))

    def allcommands(self):
        if not self.is_admin():
            return

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

    def remove_admin(self):
        if not self.is_admin():
            return

        finder = re.compile(ur'([\S*]+)')
        users = finder.findall(self.msg)
        users[0] = None
        users[1] = None
        users[2] = None
        for user in users:
            if user is None or user not in admins in user.lower():
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
            self.client.describe(
                self.channel,
                "has %s mysterious admins" % str(
                    len(admins)))
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

        chan = self.channel
        if chan == "gcibot":
            chan = self.human_user

        self.pending_msgs.append([self.channel,
                                  to,
                                  self.human_user,
                                  message,
                                  datetime.datetime.now().strftime("%H:%M %D")])

        self.client.msg(chan, "I'll wait for the user.")

    def pending_memos(self):
        pending = []
        for memo in self.pending_msgs:
            if memo[2] == self.human_user:
                pending.append(
                    "'%s' to %s at %s" %
                    (memo[3], memo[1], memo[4]))

        self.client.msg(self.human_user, str(pending))

    def all_memos(self):
        if not self.is_admin():
            return

        pending = []
        for memo in self.pending_msgs:
            pending.append(
                "'%s' to %s at %s" %
                (memo[3], memo[1], memo[4]))

        self.client.msg(self.human_user, str(pending))

    def nick(self):
        if not self.is_admin():
            return

        finder = re.compile(ur'!nick ([\S*]+)')
        nicknames = finder.findall(self.msg.lower())

        for nick in nicknames:
            self.client.setNick(nick)

    def you_can_stand(self):
        return "under my umbrella (ella, ella, eh, eh)"

    def i_rock(self):
        return "%s, sure.." % self.human_user

    def you_rock(self):
        return "%s, I know :)" % self.human_user

    def register(self, ignore_admin=False):
        if not ignore_admin:
            if not self.is_admin():
                return

        for blah in range(0, 2):
            self.client.msg(
                "NickServ",
                "identify " +
                data.username +
                " " +
                data.password)
            self.client.msg("NickServ", "release " + data.nickname)
            self.client.setNick(data.nickname)

    def svineet(self):
        if not self.is_admin():
            return

        for x in range(0, 5):
            self.client.msg("#poxip", "@svineet, hi m8, how's your gf??")
            self.client.msg(
                "svineet",
                "hi m8, how's your gf?? are you even alive?????")
