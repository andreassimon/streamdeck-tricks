import logging
import os

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

import threading

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


class NullKey:

    def update_key_image(self, _image):
        pass

    def set_callback(self, _callback):
        pass


class NullDeck:

    def get_key(self, key):
        return NullKey()

    def exit(self):
        pass


class StreamDecks:

    def __init__(self):
        self.streamdecks = list(map(StreamDeck, DeviceManager().enumerate()))

        print("Found {} Stream Deck(s).\n".format(len(self.streamdecks)))

        if len(self.streamdecks) > 0:
            self.current_deck = self.streamdecks[0]
            self.current_deck.initialize()
        else:
            self.current_deck = NullDeck()

    def items(self):
        return self.streamdecks


class StreamDeckKey:
    def __init__(self, deck, key):
        self.icon = None
        self.render_active = False
        self.deck = deck
        self.key = key
        self._callback = None

    def set_callback(self, cb):
        self._callback = cb

    def callback(self, key_down):
        if self._callback:
            self._callback(self, key_down)
        else:
            logging.info('No callback for key {}'.format(self.key))

    def set_render_active(self, render_active):
        self.render_active = render_active
        self.update_key_image()

    def set_key_image(self, image):
        # # Determine what icon and label to use on the generated key.
        # key_style = get_key_style(deck, key, state)
        #
        # # Generate the custom key with the requested image and label.
        # image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

        # Use a scoped-with on the deck to ensure we're the only thread using it
        # right now.
        self.icon = os.path.join(MODULE_PATH, image)
        self.update_key_image()
        return self

    def execute_command(self, command):
        def execute_command_callback(key, key_down):
            if key_down:
                os.system(command)

        self.set_callback(execute_command_callback)
        return self

    def switch_scene(self, obs, scene_name):
        def switch_scene_callback(key, key_down):
            if key_down:
                obs.switch_scene(scene_name)

        self.set_callback(switch_scene_callback)
        return self

    def replay_media(self, obs, media_name):
        def replay_media_callback(key, key_down):
            if key_down:
                obs.replay_media(media_name)

        self.set_callback(replay_media_callback)
        return self

    def toggle_mute(self, obs, mic_name):
        def toggle_mute_callback(key, key_down):
            if key_down:
                obs.toggle_mute(mic_name)

        self.set_callback(toggle_mute_callback)
        return self

    def update_key_image(self):
        image = self.render_key_image(self.icon, self.render_active)

        with self.deck:
            # Update requested key with the generated image.
            self.deck.set_key_image(self.key, image)

        return self

    def render_key_image(self, icon_filename, render_active):
        # font_filename = None
        # label_text = None

        # Resize the source image asset to best-fit the dimensions of a single key,
        # leaving a margin at the bottom so that we can draw the key title
        # afterwards.
        icon = Image.open(icon_filename)
        image = PILHelper.create_scaled_image(self.deck, icon, margins=[0, 0, 0, 0])

        # # Load a custom TrueType font and use it to overlay the key index, draw key
        # # label onto the image a few pixels from the bottom of the key.
        # font = ImageFont.truetype(font_filename, 14)
        # draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")
        if render_active:
            draw = ImageDraw.Draw(image)
            draw.rectangle(((0, 0), (72, 72)), outline="#ff0000", width=5)

        return PILHelper.to_native_format(self.deck, image)


class StreamDeck:

    def __init__(self, deck):
        self.deck = deck
        self.keys = list()

    def initialize(self):
        # This example only works with devices that have screens.
        if not self.deck.is_visual():
            return

        self.deck.open()
        self.deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            self.deck_type(), self.get_serial_number(), self.get_firmware_version()
        ))

        self.deck.set_brightness(30)

        for key in range(self.deck.key_count()):
            self.keys.extend([StreamDeckKey(self.deck, key)])

        # Register callback function for when a key state changes.
        self.deck.set_key_callback(self.key_change_callback)

    def get_streamdeck_label(self):
        return "{} [S/N {}]".format(self.deck_type(), self.get_serial_number())

    def get_firmware_version(self):
        return self.deck.get_firmware_version()

    def get_serial_number(self):
        return self.deck.get_serial_number()

    def deck_type(self):
        return self.deck.deck_type()

    def key_change_callback(self, deck, key, key_down):
        self.get_key(key).callback(key_down)

    def exit(self):
        with self.deck:
            # Reset deck, clearing all button images.
            self.deck.reset()

            # Close deck handle, terminating internal worker threads.
            self.deck.close()

    def get_key(self, key):
        return self.keys[key]
