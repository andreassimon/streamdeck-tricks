#!/usr/bin/python

import os

import signal
import aioconsole

import logging
import logging.config

from appindicator import AppIndicator

appindicator = None

from obs import OBS


def obs_error_callback(error):
    # TODO: Notify about error message
    appindicator.tray_error(error)


obs = OBS(obs_error_callback)

from streamdeck import StreamDecks

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))

logging.config.fileConfig(os.path.join(MODULE_PATH, 'logging.conf'))
logging.getLogger('PIL.PngImagePlugin').setLevel('ERROR')
logging.getLogger('simpleobsws').setLevel('INFO')
logger = logging.getLogger('streamdeck-tricks')


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
        obs.toggle_mute('Yeti')


def replay_applause(key, key_down):
    if key_down:
        obs.replay_media('Applause')


def replay_chirp(key, key_down):
    if key_down:
        obs.replay_media('Chirp')


def replay_pudel_tusch(key, key_down):
    if key_down:
        obs.replay_media('Pudel Tusch')


def take_screenshot(key, key_down):
    if key_down:
        os.system("flameshot gui")


def switch_scene_Camera(key, key_down):
    if key_down:
        obs.switch_scene('Camera')


def switch_scene_Pause(key, key_down):
    if key_down:
        obs.switch_scene('Pause')


current_deck.get_key(0).set_key_image('screenshot.png')
current_deck.get_key(0).set_callback(take_screenshot)

scene_camera_key = current_deck.get_key(2)
scene_camera_key.set_key_image('scene-camera.png')
scene_camera_key.set_callback(switch_scene_Camera)

scene_Pause_key = current_deck.get_key(3)
scene_Pause_key.set_key_image('scene-paused.png')
scene_Pause_key.set_callback(switch_scene_Pause)

mic_key = current_deck.get_key(10)
mic_key.set_key_image('Yeti-unmuted.png')
mic_key.set_callback(toggle_mute)

current_deck.get_key(12).set_key_image('cheering-crowd.png')
current_deck.get_key(12).set_callback(replay_applause)

current_deck.get_key(13).set_key_image('cricket.png')
current_deck.get_key(13).set_callback(replay_chirp)

current_deck.get_key(14).set_key_image('poodle-flourish.png')
current_deck.get_key(14).set_callback(replay_pudel_tusch)


async def on_inputmutestatechanged(eventData):
    # eventData: {'inputMuted': False, 'inputName': 'Mic/Aux'}
    if eventData['inputMuted']:
        # print("\n\n{} is now muted".format(eventData['inputName']))
        mic_key.set_key_image('Yeti-muted.png')

    else:
        # print("\n\n{} is now unmuted".format(eventData['inputName']))
        mic_key.set_key_image('Yeti-unmuted.png')


async def on_CurrentProgramSceneChanged(eventData):
    # eventData: {'sceneName': 'Camera'}
    print('on_CurrentProgramSceneChanged')
    render_Camera_active = False
    render_Pause_active = False
    if eventData['sceneName'] == 'Camera':
        print('Switch to Camera button')
        render_Camera_active = True

    if eventData['sceneName'] == 'Pause':
        print('Switch to Pause button')
        render_Pause_active = True

    scene_camera_key.set_render_active(render_Camera_active)
    scene_Pause_key.set_render_active(render_Pause_active)


if __name__ == "__main__":
    appindicator = AppIndicator(decks, quit)
    obs.start()
    obs.register_event_callback(on_inputmutestatechanged, 'InputMuteStateChanged')
    obs.register_event_callback(on_CurrentProgramSceneChanged, 'CurrentProgramSceneChanged')
    if len(decks.items()) == 0:
        appindicator.no_decks_found()

    # appindicator.start() MUST COME LAST
    # because it blocks the main thread so that no actions
    # after this point will be executed
    try:
        appindicator.start()
    except Exception as error:
        logger.info(error)
