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

from commands import Commands
from task_data import TaskFinder
import logging
import data
import sys

from twisted.internet import reactor, protocol
from twisted.words.protocols import irc


logging.basicConfig(level=logging.DEBUG)


class GCIBot(irc.IRCClient):
    nickname = data.nickname
    username = data.username
    password = data.password
    channels = []

    def __init__(self):
        self.commands = Commands(self)
        self.tasks_finder = TaskFinder(self)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def joined(self, channel):
        self.channels.append(channel)

    def left(self, channel):
        self.channels.remove(channel)

    def signedOn(self):
        for c in self.factory.channels:
            self.join(c)

    def privmsg(self, user, channel, msg):
        tasks = []
        result = self.commands.process_msg(msg, channel, user)
        if result:
            tasks = self.tasks_finder.process_msg(msg, channel, user)
            for task in tasks:
                self.msg(channel, task)

        self.check_memo(user, channel)

    def userJoined(self, user, channel):
        self.check_memo(user, channel)

    def check_memo(self, user, channel):
        human_user = user.split('!', 1)[0].lower()
        msgs_to_remove = []
        for msg in self.commands.pending_msgs:
            if msg[1].lower() == human_user:
                chan = msg[0]
                if chan == "gcibot":
                    self.msg(
                        human_user,
                        "Message from '%s': %s" % (msg[2],
                                                   msg[3]))
                else:
                    self.msg(
                        human_user,
                        "Message from '%s' in channel '%s': %s" % (msg[2],
                                                                   chan,
                                                                   msg[3]))
                msgs_to_remove.append(msg)

        for msg in msgs_to_remove:
            self.commands.pending_msgs.remove(msg)


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
    reactor.connectTCP("irc.freenode.net", 6667, f)
    logging.info('** Connected to server **')
    logging.info('** Channels: %s **' % ", ".join(sys.argv[1:]))
    reactor.run()
