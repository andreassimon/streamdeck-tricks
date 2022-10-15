import os

import asyncio

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

import threading


MODULE_PATH = os.path.dirname(os.path.realpath(__file__))


class StreamDecks:

    def __init__(self):
        self.streamdecks = DeviceManager().enumerate()

        print("Found {} Stream Deck(s).\n".format(len(self.streamdecks)))

        for index, deck in enumerate(self.streamdecks):
            StreamDeck().initialize(deck)


class StreamDeck:

    def initialize(self, deck):
        # This example only works with devices that have screens.
        if not deck.is_visual():
            return

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
        self.update_key_image(deck, 0, 'muted.png')
        self.update_key_image(deck, 0, 'unmuted.png')

        # Register callback function for when a key state changes.
        deck.set_key_callback(self.key_change_callback)


    def update_key_image(self, deck, key, image):
        # # Determine what icon and label to use on the generated key.
        # key_style = get_key_style(deck, key, state)
        #
        # # Generate the custom key with the requested image and label.
        # image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

        # Use a scoped-with on the deck to ensure we're the only thread using it
        # right now.
        icon = os.path.join(MODULE_PATH, image)
        image = self.render_key_image(deck, icon)

        with deck:
            # Update requested key with the generated image.
            deck.set_key_image(key, image)



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


    def key_change_callback(self, deck, key, key_down):
        # Print new key state
        print("Deck {} Key {} = {}".format(deck.id(), key, key_down), flush=True)
        print("{} threads active; current: {}".format(threading.active_count(), threading.current_thread().name))
        if key == 0 and key_down:
            # asyncio.run_coroutine_threadsafe(obs_toggle_mute('Mic/Aux'), obs_event_loop)
            self.update_key_image(deck, key, 'muted.png')
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

