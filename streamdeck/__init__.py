import os

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

import threading


MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


class StreamDecks:

    def __init__(self):
        self.streamdecks = list(map(StreamDeck, DeviceManager().enumerate()))

        print("Found {} Stream Deck(s).\n".format(len(self.streamdecks)))

        if len(self.streamdecks) > 0:
            self.current_deck = self.streamdecks[0]
            self.current_deck.initialize()

    def items(self):
        return self.streamdecks


class StreamDeckKey:
    def __init__(self, deck, key):
        self.deck = deck
        self.key = key
        self._callback = None

    def set_callback(self, cb):
        self._callback = cb

    def callback(self, key_down):
        self._callback(self, key_down)

    def update_key_image(self, image):
        # # Determine what icon and label to use on the generated key.
        # key_style = get_key_style(deck, key, state)
        #
        # # Generate the custom key with the requested image and label.
        # image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

        # Use a scoped-with on the deck to ensure we're the only thread using it
        # right now.
        icon = os.path.join(MODULE_PATH, image)
        image = self.render_key_image(self.deck, icon)

        with self.deck:
            # Update requested key with the generated image.
            self.deck.set_key_image(self.key, image)

    def render_key_image(self, deck, icon_filename, font_filename=None, label_text=None):
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
        # Print new key state
        print("Deck {} Key {} = {}".format(deck.id(), key, key_down), flush=True)
        print("{} threads active; current: {}".format(threading.active_count(), threading.current_thread().name))
        self.get_key(key).callback(key_down)
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

    def get_key(self, key):
        return self.keys[key]

