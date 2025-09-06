import json

from loguru import logger

from src.app.config.settings import settings
from src.app.infrastructure.messaging.mq_client import mq_client
from src.app.interfaces.grpc.pb.debug import debug_pb2 as pb2
from google.protobuf.json_format import MessageToJson

from src.app.interfaces.grpc.pb.debug.debug_pb2_grpc import DebugServiceServicer


class DebugService(DebugServiceServicer):
    async def SendMessage(self, request, context) -> pb2.MessageResp:  # type: ignore
        data_raw = MessageToJson(request.data) or "{}"
        data = json.loads(data_raw)
        _, data_type_ = data.pop("@type", "").split("/")
        event = request.event
        await mq_client.produce_messages(
            messages=[{"event": event, "data": data}],
            queue_name=settings.DEFAULT_QUEUE,
            exchanger_name=settings.DEFAULT_EXCHANGER,
        )
        logger.debug(f"Sent message `{event}` with data {str(data)}")
        return pb2.MessageResp(status=True, message="OK")  # type: ignore
