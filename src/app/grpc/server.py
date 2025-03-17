import os

import grpc
import asyncio
from concurrent import futures
from loguru import logger
from src.app.config.settings import settings, LaunchMode
from src.app.grpc.pb.debug import debug_pb2_grpc
from src.app.grpc.pb.example import example_pb2_grpc
from src.app.grpc.services.debug_service import DebugService
from src.app.grpc.services.example_service import ExampleService


async def serve() -> None:
    interceptors: list = []
    max_workers = int(os.cpu_count() * 1.5)  # type: ignore
    if settings.LAUNCH_MODE != LaunchMode.PROD.value:
        max_workers = 2
    server = grpc.aio.server(
        migration_thread_pool=futures.ThreadPoolExecutor(max_workers=max_workers), interceptors=interceptors
    )
    debug_pb2_grpc.add_DebugServiceServicer_to_server(DebugService(), server)
    example_pb2_grpc.add_ExampleServiceServicer_to_server(ExampleService(), server)
    server.add_insecure_port(settings.GRPC_URL)
    await server.start()
    logger.info(f"GRPC server started {settings.GRPC_URL} on {max_workers} workers")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
