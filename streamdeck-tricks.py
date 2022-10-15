#!/usr/bin/python

import os

import signal
import aioconsole
import argparse

import logging

logging.basicConfig(filename="streamdeck-tricks.log", level=logging.DEBUG)
import asyncio
import simpleobsws
import threading

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

from appindicator import AppIndicator

appindicator = AppIndicator()
from obs import OBS
from streamdeck import StreamDeck

# Initialize parser
parser = argparse.ArgumentParser(description="Adding description")
parser.add_argument('--obs-ws-url',
                    default='ws://localhost:4455',
                    help='The WebSocket of OBS to connect to')
parser.add_argument('--obs-ws-password',
                    default='6pNsEcAXBOn0nHrU',
                    help='The password to connect to the WebSocket of OBS')
args = parser.parse_args()

GENERAL = (1 << 0)
SCENES = (1 << 2)
INPUTS = (1 << 3)
OUTPUTS = (1 << 6)
MEDIA_INPUTS = (1 << 8)

parameters = simpleobsws.IdentificationParameters()  # Create an IdentificationParameters object
parameters.eventSubscriptions = GENERAL | SCENES | INPUTS | OUTPUTS | MEDIA_INPUTS

obs = simpleobsws.WebSocketClient(url=args.obs_ws_url,
                                  password=args.obs_ws_password,
                                  identification_parameters=parameters)  # Every possible argument has been passed, but none are required. See lib code for defaults.

CURRPATH = os.path.dirname(os.path.realpath(__file__))


async def on_event(eventType, eventData):
    # Print the event data. Note that `update-type` is also provided in the data
    # print('New event! Type: {} | Raw Data: {}'.format(eventType, eventData))
    pass


async def on_switchscenes(eventData):
    print('Scene switched to "{}".'.format(eventData['sceneName']))


async def on_inputmutestatechanged(eventData):
    # Data: {'inputMuted': False, 'inputName': 'Mic/Aux'}
    if eventData['inputMuted']:
        print("\n\n{} is now muted".format(eventData['inputName']))
        streamdecks = DeviceManager().enumerate()
        for index, deck in enumerate(streamdecks):
            # This example only works with devices that have screens.
            if not deck.is_visual():
                continue
            print("{} button 0: muted.png".format(deck.id()))
            print("{} threads active; current: {}".format(threading.active_count(), threading.current_thread().name))
            update_key_image(deck, 0, 'muted.png')

    else:
        print("\n\n{} is now unmuted".format(eventData['inputName']))
        streamdecks = DeviceManager().enumerate()
        for index, deck in enumerate(streamdecks):
            # This example only works with devices that have screens.
            if not deck.is_visual():
                continue
            print("{} button 0: unmuted.png".format(deck.id()))
            print("{} threads active; current: {}".format(threading.active_count(), threading.current_thread().name))
            update_key_image(deck, 0, 'unmuted.png')


async def obs_init_websocket():
    try:
        await obs.connect()
        await obs.wait_until_identified()

        request = simpleobsws.Request('GetVersion')

        ret = await obs.call(request)

        if ret.ok():
            logging.debug("GetVersion succeeded! Response data: {}".format(ret.responseData))

    except OSError as error:
        print('\n\nERROR Connecting')
        print(error)
        appindicator.tray_error(None)


async def obs_switch_scene(scene_name):
    request = simpleobsws.Request(requestType='SetCurrentProgramScene', requestData=dict(sceneName=scene_name))

    ret = await obs.call(request)
    if not ret.ok():
        print("SetCurrentProgramScene failed! Response data: {}".format(ret.responseData))


async def obs_toggle_mute(input_name):
    request = simpleobsws.Request(requestType='ToggleInputMute', requestData=dict(inputName=input_name))

    ret = await obs.call(request)
    if not ret.ok():
        print("ToggleInputMute failed! Response data: {}".format(ret.responseData))


async def obs_replay_media(input_name):
    request = simpleobsws.Request(
        requestType='TriggerMediaInputAction',
        requestData=dict(
            inputName=input_name,
            mediaAction='OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART'
        ))
    ret = await obs.call(request)
    if not ret.ok():
        print("TriggerMediaInputAction failed! Response data: {}".format(ret.responseData))


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




obs_event_loop = asyncio.get_event_loop()
streamdeck_event_loop = asyncio.get_event_loop()


def key_change_callback(deck, key, key_down):
    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, key_down), flush=True)
    print("{} threads active; current: {}".format(threading.active_count(), threading.current_thread().name))
    if key == 0 and key_down:
        asyncio.run_coroutine_threadsafe(obs_toggle_mute('Mic/Aux'), obs_event_loop)
        update_key_image(deck, key, 'muted.png')
    # # Update the key image based on the new key state.
    # update_key_image(deck, key, state)
    #
    # # Check if the key is changing to the pressed state.
    # if state:
    #     key_style = get_key_style(deck, key, state)
    #
    #     # When an exit button is pressed, close the application.
    #     if key_style["name"] == "exit":
    #         # Use a scoped-with on the deck to ensure we're the only thread
    #         # using it right now.
    #         with deck:
    #             # Reset deck, clearing all button images.
    #             deck.reset()
    #
    #             # Close deck handle, terminating internal worker threads.
    #             deck.close()


def update_key_image(deck, key, image):
    # # Determine what icon and label to use on the generated key.
    # key_style = get_key_style(deck, key, state)
    #
    # # Generate the custom key with the requested image and label.
    # image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    icon = os.path.join(CURRPATH, 'streamdeck', image)
    image = render_key_image(deck, icon)

    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)


def render_key_image(deck, icon_filename, font_filename=None, label_text=None):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 0, 0])

    # # Load a custom TrueType font and use it to overlay the key index, draw key
    # # label onto the image a few pixels from the bottom of the key.
    # draw = ImageDraw.Draw(image)
    # font = ImageFont.truetype(font_filename, 14)
    # draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_format(deck, image)


async def streamdeck_initialize():
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        # This example only works with devices that have screens.
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()
        ))

        # Set initial screen brightness to 30%.
        deck.set_brightness(30)

        # # Set initial key images.
        # for key in range(deck.key_count()):
        #     update_key_image(deck, key, False)
        update_key_image(deck, 0, 'muted.png')
        update_key_image(deck, 0, 'unmuted.png')

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)


signal.signal(signal.SIGINT, sigint_handler)
if __name__ == "__main__":
    appindicator.start()
    # event_loop.create_task(console_keys())

    obs_event_loop.run_until_complete(obs_init_websocket())
    obs_event_loop.run_until_complete(obs_toggle_mute('Mic/Aux'))

    # By not specifying an event to listen to, all events are sent to this callback.
    obs.register_event_callback(on_event)
    obs.register_event_callback(on_switchscenes, 'CurrentProgramSceneChanged')
    obs.register_event_callback(on_inputmutestatechanged, 'InputMuteStateChanged')
    streamdeck_event_loop.run_until_complete(streamdeck_initialize())
    obs_event_loop.run_forever()
    # streamdeck_event_loop.run_forever()
