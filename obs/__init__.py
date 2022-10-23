import argparse
import asyncio
import logging
import simpleobsws
import threading

logger = logging.getLogger('streamdeck-tricks')

GENERAL = (1 << 0)
SCENES = (1 << 2)
INPUTS = (1 << 3)
OUTPUTS = (1 << 6)
MEDIA_INPUTS = (1 << 8)

parameters = simpleobsws.IdentificationParameters()  # Create an IdentificationParameters object
parameters.eventSubscriptions = GENERAL | SCENES | INPUTS | OUTPUTS | MEDIA_INPUTS

# Initialize parser
parser = argparse.ArgumentParser(description="Adding description")
parser.add_argument('--obs-ws-url',
                    default='ws://localhost:4455',
                    help='The WebSocket of OBS to connect to')
parser.add_argument('--obs-ws-password',
                    default='6pNsEcAXBOn0nHrU',
                    help='The password to connect to the WebSocket of OBS')
args = parser.parse_args()


class OBSInitExeption(Exception):
    pass


class OBS:

    def __init__(self, error_callback):
        self.obs = None
        self.obs_event_loop = None
        self.obs_lock = threading.Lock()
        self.obs_lock.acquire()
        self.error_callback = error_callback

    def start(self):
        logger.debug('obs.OBS.start')
        obs_thread = threading.Thread(target=self.obs_thread, name="OBS-Communication-Thread")
        obs_thread.start()

    def obs_thread(self):
        logger.debug('obs_thread started')
        self.obs_event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.obs_event_loop)

        logger.debug('Trying to instantiate simpleobsws.WebSocketClient')
        self.obs = simpleobsws.WebSocketClient(url=args.obs_ws_url,
                                               password=args.obs_ws_password,
                                               identification_parameters=parameters)
        logger.debug('Instantiated simpleobsws.WebSocketClient')

        self.obs_event_loop.run_until_complete(self.obs_init_websocket())
        self.obs_lock.release()
        self.toggle_mute('Mic/Aux')
        # By not specifying an event to listen to, all events are sent to this callback.
        with self.obs_lock:
            self.obs.register_event_callback(self.on_event)
            self.obs.register_event_callback(self.on_switchscenes, 'CurrentProgramSceneChanged')

        self.obs_event_loop.run_forever()

    def register_event_callback(self, callback, event: str = None):
        with self.obs_lock:
            self.obs.register_event_callback(callback, event)

    async def obs_init_websocket(self):
        try:
            logger.debug('trying to connect')
            await self.obs.connect()
            logger.debug('connection established')
            await self.obs.wait_until_identified()

            request = simpleobsws.Request('GetVersion')

            ret = await self.obs.call(request)

            if ret.ok():
                logger.debug("GetVersion succeeded! Response data: {}".format(ret.responseData))

        except OSError as error:
            self.error_callback(OBSInitExeption('ERROR Connecting', error))

    def exit(self):
        if self.obs:
            asyncio.run_coroutine_threadsafe(self.obs.disconnect(), self.obs_event_loop)
        if self.obs_event_loop:
            self.obs_event_loop.stop()

    async def on_event(self, eventType, eventData):
        logger.debug('New event! Type: {} | Raw Data: {}'.format(eventType, eventData))
        pass

    async def on_switchscenes(self, eventData):
        logger.debug('Scene switched to "{}".'.format(eventData['sceneName']))

    def switch_scene(self, scene_name):
        request = simpleobsws.Request(requestType='SetCurrentProgramScene', requestData=dict(sceneName=scene_name))

        future = asyncio.run_coroutine_threadsafe(self.obs.call(request), self.obs_event_loop)
        try:
            ret = future.result(1)
            if not ret.ok():
                logger.debug("SetCurrentProgramScene failed! Response data: {}".format(ret.responseData))
        except Exception as error:
            logger.exception("SetCurrentProgramScene")

    def get_source_screenshot(self, source_name):
        request = simpleobsws.Request(requestType='GetSourceScreenshot', requestData=dict(
            sourceName=source_name,
            imageFormat="png",
            imageFilePath="/home/andreas/Dropbox/OBS/streamdeck-py/screenshot.png"
        ))
        return self.execute_request(request)['imageData'][22:]

    def execute_request(self, request):
        with self.obs_lock:
            future = asyncio.run_coroutine_threadsafe(self.obs.call(request), self.obs_event_loop)
            try:
                ret = future.result(5)
                if not ret.ok():
                    logger.debug("{} failed! Response data: {}".format(request.requestType, ret.responseData))
                else:
                    logger.debug("{} succeeded! Response data: {}".format(request.requestType, ret.responseData))
                return ret.responseData
            except:
                logger.exception(request.requestType)


    def toggle_mute(self, input_name):
        if not self.obs:
            logger.error('streamdeck-tricks is not connected to OBS')
            self.error_callback(OBSInitExeption('ERROR Connecting'))
            return

        request = simpleobsws.Request(requestType='ToggleInputMute', requestData=dict(inputName=input_name))

        future = asyncio.run_coroutine_threadsafe(self.obs.call(request), self.obs_event_loop)
        try:
            ret = future.result(1)
            if not ret.ok():
                logger.debug("ToggleInputMute failed! Response data: {}".format(ret.responseData))
        except Exception as error:
            logger.exception('ToggleInputMute')

    def replay_media(self, input_name):
        if not self.obs:
            logger.error('streamdeck-tricks is not connected to OBS')
            self.error_callback(OBSInitExeption('ERROR Connecting'))
            return

        request = simpleobsws.Request(
            requestType='TriggerMediaInputAction',
            requestData=dict(
                inputName=input_name,
                mediaAction='OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART'
            ))
        future = asyncio.run_coroutine_threadsafe(self.obs.call(request), self.obs_event_loop)
        try:
            ret = future.result(1)
            if not ret.ok():
                logger.debug("TriggerMediaInputAction failed! Response data: {}".format(ret.responseData))
        except Exception as error:
            logger.exception('TriggerMediaInputAction')

    def disable_source_filter(self, source_name, filter_name):
        self.set_source_filter_enabled(source_name, filter_name, False)

    def enable_source_filter(self, source_name, filter_name):
        self.set_source_filter_enabled(source_name, filter_name, True)

    def set_source_filter_enabled(self, source_name, filter_name, filter_enabled):
        return self.execute_request(simpleobsws.Request(requestType='SetSourceFilterEnabled', requestData=dict(
            sourceName=source_name,
            filterName=filter_name,
            filterEnabled=filter_enabled
        )))

    def set_source_filter_settings(self, source_name, filter_name, filter_settings=None):
        if filter_settings is None:
            filter_settings = dict()
        return self.execute_request(simpleobsws.Request(requestType='SetSourceFilterSettings', requestData=dict(
            sourceName=source_name,
            filterName=filter_name,
            filterSettings=filter_settings
        )))
