import os

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator

import signal
import aioconsole
import argparse

import logging


logging.basicConfig(filename="main.log", level=logging.DEBUG)
import asyncio
import simpleobsws

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

ws = simpleobsws.WebSocketClient(url=args.obs_ws_url,
                                 password=args.obs_ws_password,
                                 identification_parameters=parameters)  # Every possible argument has been passed, but none are required. See lib code for defaults.


async def on_event(eventType, eventData):
    # Print the event data. Note that `update-type` is also provided in the data
    # print('New event! Type: {} | Raw Data: {}'.format(eventType, eventData))
    pass


async def on_switchscenes(eventData):
    print('Scene switched to "{}".'.format(eventData['sceneName']))


async def on_inputmutestatechanged(eventData):
    # Data: {'inputMuted': False, 'inputName': 'Mic/Aux'}
    if eventData['inputMuted']:
        print("{} is now muted".format(eventData['inputName']))
    else:
        print("{} is now unmuted".format(eventData['inputName']))


async def init():
    await ws.connect()
    # ConnectionRefusedError
    await ws.wait_until_identified()

    request = simpleobsws.Request('GetVersion')  # Build a Request object

    ret = await ws.call(request)  # Perform the request
    if ret.ok():  # Check if the request succeeded
        print("GetVersion succeeded! Response data: {}".format(ret.responseData))



async def switch_scene(scene_name):
    request = simpleobsws.Request(requestType='SetCurrentProgramScene', requestData=dict(sceneName=scene_name))

    ret = await ws.call(request)
    if not ret.ok():
        print("SetCurrentProgramScene failed! Response data: {}".format(ret.responseData))


async def toggle_mute(input_name):
    request = simpleobsws.Request(requestType='ToggleInputMute', requestData=dict(inputName=input_name))

    ret = await ws.call(request)
    if not ret.ok():
        print("ToggleInputMute failed! Response data: {}".format(ret.responseData))


async def replay_media(input_name):
    request = simpleobsws.Request(
        requestType='TriggerMediaInputAction',
        requestData=dict(
            inputName=input_name,
            mediaAction='OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART'
        ))
    ret = await ws.call(request)
    if not ret.ok():
        print("TriggerMediaInputAction failed! Response data: {}".format(ret.responseData))


async def console_keys():
    while True:
        response = await aioconsole.ainput('Scenes: [c]amera, [a]vatar, [l]eitplanken, [m]ute, [t]usch: ')
        if response == 'c':
            await switch_scene('Camera')
        elif response == 'a':
            await switch_scene('Avatar')
        elif response == 'l':
            await switch_scene('Leitplanken')
        elif response == 'm':
            await toggle_mute('Mic/Aux')
        elif response == 't':
            await replay_media('Pudel Tusch')


def sigint_handler(signum, frame):
    quit(None)


def tray_menu():
    menu = gtk.Menu()

    show_logs_tray = gtk.MenuItem(label='Show Logs')
    show_logs_tray.connect('activate', tray_show_logs)
    menu.append(show_logs_tray)

    exit_tray = gtk.MenuItem(label='Quit')
    exit_tray.connect('activate', quit)
    menu.append(exit_tray)

    menu.show_all()
    return menu


def tray_show_logs(_):
    os.system("deepin-appstore %U")


def quit(_):
    print("\n\nExit")
    gtk.main_quit()
    exit(0)


def tray_initialize():
    indicator = appindicator.Indicator.new("customtray", "/home/andreas/Dropbox/OBS/streamdeck-py/elgato_logo_icon.png",
                                           appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(tray_menu())
    gtk.main()


signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    tray_initialize()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    # By not specifying an event to listen to, all events are sent to this callback.
    ws.register_event_callback(on_event)
    ws.register_event_callback(on_switchscenes, 'CurrentProgramSceneChanged')
    ws.register_event_callback(on_inputmutestatechanged, 'InputMuteStateChanged')
    loop.create_task(console_keys())
    loop.run_forever()
