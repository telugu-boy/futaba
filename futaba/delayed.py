#
# delayed.py
#
# futaba - A Discord Mod bot for the Programming server
# Copyright (c) 2017-2019 Jake Richardson, Ammon Smith, jackylam5
#
# futaba is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

"""
An asynchronous queue that takes in lower-priority discord.py API events
and sends them slowly over time. This prevents the bot from becoming
slowed down or gridlocked over long-running or mass operations.
"""

import asyncio
import inspect
import logging

logger = logging.getLogger(__name__)


class DelayedQueue:
    __slots__ = ("bracket_size", "rate", "max_delay", "queue")

    def __init__(self, config):
        self.bracket_size = config.delay_bracket_size
        self.rate = config.delay_rate
        self.max_delay = config.delay_max
        self.queue = asyncio.Queue()

    def start(self, eventloop):
        eventloop.create_task(self.main_loop())

    def push(self, coro):
        assert inspect.iscoroutine(coro)
        self.queue.put_nowait(coro)

    async def main_loop(self):
        while True:
            logger.debug("Waiting for new delayed event")
            coro = await self.queue.get()
            await coro

            logger.debug(
                "Sleeping for %.1f seconds until next delayed event", self.delay
            )
            await asyncio.sleep(self.delay)

    @property
    def delay(self):
        rate = self.queue.qsize() // self.bracket_size
        return min(rate * self.rate, self.max_delay)

    def __len__(self):
        return self.queue.qsize()
