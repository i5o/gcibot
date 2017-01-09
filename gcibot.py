#!/usr/bin/env python
# -*- coding: utf-8 -*-
# GCI bot.
# Parse tasks data and show info about them
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

from task_data import TaskFinder
import logging
import data
import sys
import subprocess

from twisted.internet import reactor, protocol
from twisted.words.protocols import irc


logging.basicConfig(level=logging.DEBUG)


class GCIBot(irc.IRCClient):
    nickname = data.nickname
    username = data.username
    password = data.password
    channels = []

    def __init__(self):
        self.tasks_finder = TaskFinder(self)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def joined(self, channel):
        if channel not in self.channels:
            self.channels.append(channel)

    def left(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)

    def signedOn(self):
        for c in self.factory.channels:
            self.join(c)

    def privmsg(self, user, channel, msg):
        tasks = self.tasks_finder.process_msg(msg, channel, user)
        for task in tasks:
            self.msg(channel, task)

        talking_to_me = msg.startswith(self.nickname + ":") \
            or msg.startswith(self.nickname + ",") \
            or msg.startswith(self.nickname + " ")

        if talking_to_me and "uptime" in msg.lower():
            self.uptime(channel)

    def uptime(self, channel):
        host = subprocess.check_output("hostname").replace("\n", " ")
        up = subprocess.check_output("uptime").replace("\n", " ")
        self.msg(channel, "%s %s" % (host, up))


class BotFactory(protocol.ClientFactory):

    def __init__(self, channels):
        self.channels = channels

    def buildProtocol(self, addr):
        p = GCIBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        logging.error("** Conection failed ** ")
        reactor.stop()


if __name__ == '__main__':
    logging.info('** Starting GCIBot **')
    f = BotFactory(sys.argv[1:])
    reactor.connectTCP(data.server, data.port, f)
    logging.info('** Connected to server **')
    logging.info('** Channels: %s **' % ", ".join(sys.argv[1:]))
    reactor.run()
