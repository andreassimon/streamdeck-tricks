#!/usr/bin/python

import os

import signal
import aioconsole

import logging

logging.basicConfig(filename="streamdeck-tricks.log", level=logging.DEBUG)
import threading

from appindicator import AppIndicator
appindicator = None

from obs import OBS
obs = OBS()

from streamdeck import StreamDecks

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
    obs.exit()
    # Wait until all application threads have terminated (for this example,
    # this is when all deck handles are closed).
    # for t in threading.enumerate():
    #     try:
    #         print("Trying to join '{}'".format(t.name))
    #         t.join()
    #         print("Joined {}".format(t.name))
    #     except RuntimeError as error:
    #         print("{} '{}'".format(error, t.name))
    #         pass

    appindicator.exit()
    exit(0)


current_deck = None
signal.signal(signal.SIGINT, sigint_handler)

def toggle_mute(key, key_down):
    if key_down:
        obs.obs_toggle_mute('Mic/Aux')
        key.update_key_image('muted.png')
    else:
        key.update_key_image('unmuted.png')
    # asyncio.run_coroutine_threadsafe(obs_toggle_mute('Mic/Aux'), obs_event_loop)


if __name__ == "__main__":
    # event_loop.create_task(console_keys())
    decks = StreamDecks()
    current_deck = decks.current_deck
    current_deck.get_key(0).update_key_image('muted.png')
    current_deck.get_key(0).update_key_image('unmuted.png')
    current_deck.get_key(0).set_callback(toggle_mute)
    obs.start()
    appindicator = AppIndicator(decks)
    appindicator.start()
