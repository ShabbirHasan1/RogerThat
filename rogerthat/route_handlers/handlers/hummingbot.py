from quart import (
    abort,
    jsonify,
)
from rogerthat.models.web_request import web_request
from rogerthat.models.wss_request import wss_request
from rogerthat.db.models.tradingview_event import tradingview_event
from rogerthat.utils.logger import logger


class route_handlers_hummingbot:
    def __init__(self):
        pass

    async def route_handler_hummingbot(self, quart_request):
        request = web_request(from_quart=quart_request)
        await request.build_request_args()
        valid_request = await request.check_is_valid(for_hbot_api=True)
        if valid_request:
            latest_event = await tradingview_event.fetch_latest()
            if latest_event:
                return jsonify(latest_event.to_dict)
            return jsonify(None)
        return abort(401)


class wss_handlers_hummingbot:
    def __init__(self):
        pass

    async def wss_handler_hummingbot(self, ws_request, ws_queue, ws_channel=None):
        request = wss_request(from_quart=ws_request, ws_queue=ws_queue)
        valid_request = request.check_auth()
        if valid_request:
            if ws_channel:
                await logger.log(f"New websocket client connected on channel: {ws_channel}")
            else:
                await logger.log("New websocket client connected.")
            latest_event = await tradingview_event.fetch_latest(event_descriptor=ws_channel)
            await request.process_wss(latest_event)
        return abort(401)
