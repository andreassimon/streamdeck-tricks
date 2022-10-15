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


decks = StreamDecks()
current_deck = decks.current_deck


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
    current_deck.exit()
    exit(0)


signal.signal(signal.SIGINT, sigint_handler)


def toggle_mute(key, key_down):
    if key_down:
        obs.toggle_mute('Mic/Aux')


def replay_applause(key, key_down):
    if key_down:
        obs.replay_media('Applause')


def replay_chirp(key, key_down):
    if key_down:
        obs.replay_media('Chirp')


def replay_pudel_tusch(key, key_down):
    if key_down:
        obs.replay_media('Pudel Tusch')


mic_key = current_deck.get_key(14)
mic_key.update_key_image('muted.png')
mic_key.update_key_image('unmuted.png')
mic_key.set_callback(toggle_mute)

current_deck.get_key(10).update_key_image('cheering-crowd.png')
current_deck.get_key(10).set_callback(replay_applause)

current_deck.get_key(11).update_key_image('steppe.png')
current_deck.get_key(11).set_callback(replay_chirp)

current_deck.get_key(12).update_key_image('poodle-flourish.png')
current_deck.get_key(12).set_callback(replay_pudel_tusch)


async def on_inputmutestatechanged(eventData):
    # eventData: {'inputMuted': False, 'inputName': 'Mic/Aux'}
    if eventData['inputMuted']:
        # print("\n\n{} is now muted".format(eventData['inputName']))
        mic_key.update_key_image('muted.png')

    else:
        # print("\n\n{} is now unmuted".format(eventData['inputName']))
        mic_key.update_key_image('unmuted.png')


if __name__ == "__main__":
    obs.start()
    obs.register_event_callback(on_inputmutestatechanged, 'InputMuteStateChanged')
    appindicator = AppIndicator(decks, quit)
    appindicator.start()
