import grpc

from src.app.config.settings import settings
from src.app.grpc.pb.debug import debug_pb2_grpc
from src.app.grpc.pb.debug import debug_pb2 as pb2
from google.protobuf.any_pb2 import Any

def run():
    with grpc.insecure_channel(settings.GRPC_URL) as channel:
        stub = debug_pb2_grpc.DebugServiceStub(channel)
        data = pb2.SayMeqDataReq()
        
        # Pack the Struct into the Any field
        any_data = Any()
        any_data.Pack(data)
        
        # Send the request
        response = stub.SendMessage(
            pb2.MessageReq(
                event="say_meow",
                data=any_data
            )
        )
        
        data_2 = pb2.TestDataReq(year="2025", month="05")
        
        # Pack the Struct into the Any field
        any_data_2 = Any()
        any_data_2.Pack(data_2)
        
        # Send the request
        response = stub.SendMessage(
            pb2.MessageReq(
                event="test_event",
                data=any_data_2
            )
        )


if __name__ == "__main__":
    run()
