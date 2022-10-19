#!/usr/bin/python

import logging.config
import os
import signal

from obs import OBS
from appindicator import AppIndicator

appindicator = None


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


def sigint_handler(signum, frame):
    quit()


decks = StreamDecks()
current_deck = decks.current_deck


def quit(_=None):
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


current_deck.get_key(0)\
    .set_key_image('flameshot.png')\
    .execute_command('flameshot gui')

scene_camera_key = current_deck.get_key(2)
scene_camera_key \
    .set_key_image('scene-camera.png')\
    .switch_scene(obs, 'Camera')

scene_Pause_key = current_deck.get_key(3)
scene_Pause_key.set_key_image('scene-paused.png')


def switch_scene_Pause(key, key_down):
    if key_down:
        appindicator.countdown_some_minutes()
        obs.switch_scene('Pause')


scene_Pause_key.set_callback(switch_scene_Pause)


current_deck.get_key(7)\
    .set_key_image('signal-desktop.png')\
    .execute_command('signal-desktop')
current_deck.get_key(8)\
    .set_key_image('threema.png')\
    .execute_command("/usr/bin/chromium-browser --profile-directory=Default --app-id=hfcfobejdjlbgbkfiipblolhafdlkhfl")
current_deck.get_key(9)\
    .set_key_image('whatsie.png')\
    .execute_command('env BAMF_DESKTOP_FILE_HINT=/var/lib/snapd/desktop/applications/whatsie_whatsie.desktop /snap/bin/whatsie --show-window')

mic_key = current_deck.get_key(10)
mic_key\
    .set_key_image('Yeti-unmuted.png')\
    .toggle_mute(obs, 'Yeti')

current_deck.get_key(12)\
    .set_key_image('cheering-crowd.png')\
    .replay_media(obs, 'Applause')

current_deck.get_key(13)\
    .set_key_image('cricket.png')\
    .replay_media(obs, 'Chirp')

current_deck.get_key(14)\
    .set_key_image('poodle-flourish.png')\
    .replay_media(obs, 'Pudel Tusch')


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
    render_Camera_active = False
    render_Pause_active = False
    if eventData['sceneName'] == 'Camera':
        render_Camera_active = True

    if eventData['sceneName'] == 'Pause':
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
