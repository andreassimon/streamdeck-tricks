#!/usr/bin/python

import base64
import logging.config
import os
from pulse import configure_pulse
import signal

from obs import OBS
from appindicator import StreamDeckTricksGtk


def obs_error_callback(error):
    # TODO: Notify about error message
    streamdeck_tricks_gtk.show_error(error)


obs = OBS(obs_error_callback)

from streamdeck import StreamDecks, switch_scene, execute_command, toggle_mute, replay_media

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

    streamdeck_tricks_gtk.exit()
    current_deck.exit()
    exit(0)


signal.signal(signal.SIGINT, sigint_handler)

class ObsPage:
    def __init__(self, deck):
        self.streamdeck = deck
        self.streamdeck.get_key(0) \
            .set_key_image('flameshot.png') \
            .on_key_down(execute_command(['flameshot', 'gui']))

        self.scene_camera_key = self.streamdeck.get_key(2)
        self.scene_camera_key \
            .set_key_image('scene-camera.png') \
            .on_key_down(switch_scene(obs, 'Camera'))

        self.scene_Pause_key = self.streamdeck.get_key(3)
        self.scene_Pause_key.set_key_image('scene-paused.png')

        def switch_scene_Pause(key, key_down):
            if key_down:
                streamdeck_tricks_gtk.countdown_some_minutes()
                obs.switch_scene('Pause')


        self.scene_Pause_key.set_callback(switch_scene_Pause)

        self.scene_kaenguru_key = self.streamdeck.get_key(4)
        self.scene_kaenguru_key \
            .set_key_image('kaenguru.png') \
            .on_key_down(switch_scene(obs, 'Känguru'))

        self.streamdeck.get_key(5) \
            .set_key_image('teams.png') \
            .on_key_down(execute_command('teams'))
        self.streamdeck.get_key(6) \
            .set_key_image('thunderbird.png') \
            .on_key_down(execute_command('thunderbird'))
        self.streamdeck.get_key(7) \
            .set_key_image('signal-desktop.png') \
            .on_key_down(execute_command('signal-desktop'))
        self.streamdeck.get_key(8) \
            .set_key_image('threema.png') \
            .on_key_down(execute_command(
            ['/usr/bin/chromium-browser', '--profile-directory=Default', '--app-id=hfcfobejdjlbgbkfiipblolhafdlkhfl']))
        self.streamdeck.get_key(9) \
            .set_key_image('whatsie.png') \
            .on_key_down(execute_command(
            ['env', 'BAMF_DESKTOP_FILE_HINT=/var/lib/snapd/desktop/applications/whatsie_whatsie.desktop', '/snap/bin/whatsie',
             '--show-window']))

        self.mic_key = self.streamdeck.get_key(10)
        self.mic_key \
            .set_key_image('Yeti-unmuted.png') \
            .on_key_down(toggle_mute(obs, 'Yeti'))

        self.streamdeck.get_key(12) \
            .set_key_image('cheering-crowd.png') \
            .on_key_down(replay_media(obs, 'Applause'))

        self.streamdeck.get_key(13) \
            .set_key_image('cricket.png') \
            .on_key_down(replay_media(obs, 'Chirp'))

        self.streamdeck.get_key(14) \
            .set_key_image('poodle-flourish.png') \
            .on_key_down(replay_media(obs, 'Pudel Tusch'))

obs_page = ObsPage(current_deck)

async def on_inputmutestatechanged(eventData):
    # eventData: {'inputMuted': False, 'inputName': 'Mic/Aux'}
    if eventData['inputMuted']:
        # print("\n\n{} is now muted".format(eventData['inputName']))
        obs_page.mic_key.set_key_image('Yeti-muted.png')

    else:
        # print("\n\n{} is now unmuted".format(eventData['inputName']))
        obs_page.mic_key.set_key_image('Yeti-unmuted.png')


async def on_CurrentProgramSceneChanged(eventData):
    # eventData: {'sceneName': 'Camera'}
    render_Camera_active = False
    render_Kaenguru_active = False
    render_Pause_active = False
    if eventData['sceneName'] == 'Camera':
        render_Camera_active = True

    if eventData['sceneName'] == 'Känguru':
        render_Kaenguru_active = True

    if eventData['sceneName'] == 'Pause':
        render_Pause_active = True

    obs_page.scene_camera_key.set_render_active(render_Camera_active)
    obs_page.scene_kaenguru_key.set_render_active(render_Kaenguru_active)
    obs_page.scene_Pause_key.set_render_active(render_Pause_active)


if __name__ == "__main__":
    def setup_chroma_key(_streamdeck_key):
        def take_screenshot():
            def decode_base64(encoded_string):
                encoded_bytes = encoded_string.encode("ascii")
                decoded_bytes = base64.b64decode(encoded_bytes)
                return decoded_bytes

            obs.disable_source_filter("Logitech C922", "Chroma Key")
            response = obs.get_source_screenshot("Logitech C922")
            obs.enable_source_filter("Logitech C922", "Chroma Key")

            image = decode_base64(response)
            with open("get_source_screenshot.png", "wb") as file:
                file.write(image)

            return "get_source_screenshot.png"

        def chroma_key_found(key_color, radius):
            obs.set_chroma_key_properties(key_color, radius)

        streamdeck_tricks_gtk.determine_green_values_in(take_screenshot, chroma_key_found)


    streamdeck_tricks_gtk = StreamDeckTricksGtk(configure_pulse, decks, quit, setup_chroma_key)

    obs.start()
    obs.register_event_callback(on_inputmutestatechanged, 'InputMuteStateChanged')
    obs.register_event_callback(on_CurrentProgramSceneChanged, 'CurrentProgramSceneChanged')
    if len(decks.items()) == 0:
        streamdeck_tricks_gtk.no_decks_found()

    # streamdeck_tricks_gtk.start() MUST COME LAST
    # because it blocks the main thread so that no actions
    # after this point will be executed
    try:
        streamdeck_tricks_gtk.start()
    except Exception as error:
        logger.exception('streamdeck_tricks_gtk.start()')
