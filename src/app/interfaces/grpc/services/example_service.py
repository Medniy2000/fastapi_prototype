from src.app.interfaces.grpc.pb.example import example_pb2 as pb2
from src.app.interfaces.grpc.pb.example.example_pb2_grpc import ExampleServiceServicer


class ExampleService(ExampleServiceServicer):
    async def GetExample(self, request, context) -> pb2.ExampleResp:
        return pb2.ExampleResp(example_message="OK")
