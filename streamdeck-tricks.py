#!/usr/bin/python

import os

import signal
import aioconsole

import logging

logging.basicConfig(filename="streamdeck-tricks.log", level=logging.DEBUG)
import threading

from appindicator import AppIndicator
appindicator = AppIndicator()

from obs import OBS
from streamdeck import initialize_decks

CURRPATH = os.path.dirname(os.path.realpath(__file__))


async def console_keys():
    while True:
        response = await aioconsole.ainput('Scenes: [c]amera, [a]vatar, [l]eitplanken, [m]ute, [t]usch: ')
        if response == 'c':
            await obs_switch_scene('Camera')
        elif response == 'a':
            await obs_switch_scene('Avatar')
        elif response == 'l':
            await obs_switch_scene('Leitplanken')
        elif response == 'm':
            await obs_toggle_mute('Mic/Aux')
        elif response == 't':
            await obs_replay_media('Pudel Tusch')


def sigint_handler(signum, frame):
    quit(None)


def quit(_):
    print("\n\nExit")
    # Wait until all application threads have terminated (for this example,
    # this is when all deck handles are closed).
    for t in threading.enumerate():
        try:
            t.join()
        except RuntimeError:
            pass

    appindicator.exit()
    exit(0)



signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    # event_loop.create_task(console_keys())
    initialize_decks()
    OBS()
    appindicator.start()
