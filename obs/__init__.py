import asyncio
import logging
import simpleobsws


class OBS:
    pass


obs_event_loop = asyncio.get_event_loop()

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


def initialize_obs():
    obs_event_loop.run_until_complete(obs_init_websocket())
    obs_event_loop.run_until_complete(obs_toggle_mute('Mic/Aux'))
    # By not specifying an event to listen to, all events are sent to this callback.
    obs.register_event_callback(on_event)
    obs.register_event_callback(on_switchscenes, 'CurrentProgramSceneChanged')
    obs.register_event_callback(on_inputmutestatechanged, 'InputMuteStateChanged')
    obs_event_loop.run_forever()


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
        # streamdecks = DeviceManager().enumerate()
        # for index, deck in enumerate(streamdecks):
        #     # This example only works with devices that have screens.
        #     if not deck.is_visual():
        #         continue
        #     print("{} button 0: muted.png".format(deck.id()))
        #     print("{} threads active; current: {}".format(threading.active_count(), threading.current_thread().name))
        #     update_key_image(deck, 0, 'muted.png')

    else:
        print("\n\n{} is now unmuted".format(eventData['inputName']))
        # streamdecks = DeviceManager().enumerate()
        # for index, deck in enumerate(streamdecks):
        #     # This example only works with devices that have screens.
        #     if not deck.is_visual():
        #         continue
        #     print("{} button 0: unmuted.png".format(deck.id()))
        #     print("{} threads active; current: {}".format(threading.active_count(), threading.current_thread().name))
        #     update_key_image(deck, 0, 'unmuted.png')


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

