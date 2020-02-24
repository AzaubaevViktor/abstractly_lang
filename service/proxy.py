from typing import Callable, Awaitable, Any, Type

from service import Service, Message, handler


class ProxyServiceClient(Service):
    async def warm_up(self):
        # TODO: Open connection to other server
        raise NotImplementedError()

    async def _apply_task(self,
                          message: Message,
                          method: Callable[[Message], Awaitable[Any]]):
        # TODO: Memoize
        wrapped_method = self._wrap_call_method_remotely(method)
        return await super()._apply_task(
            message,
            wrapped_method
        )

    def _wrap_call_method_remotely(self, method) -> Callable:
        async def _(message):
            raise NotImplementedError()
            # TODO: serialize message data
            #   Send to server
            #   Wait for answer
            #   Deserialize data
            #   Set answer

            # TODO: If error -- return to queue
        return _

    def shutdown(self, message: Message):
        # Send to server Shutdown message
        raise NotImplementedError()


class ProxyServiceServer(Service):
    async def warm_up(self):
        # TODO: Connect to client
        #  Wait while service alive
        raise NotImplementedError()

    async def _apply_task(self,
                          message: Message,
                          method: Callable[[Message], Awaitable[Any]]):
        wrapped_method = self._wrap_call_service(method)
        return await super()._apply_task(
            message,
            wrapped_method
        )

    def _wrap_call_service(self, method) -> Callable:
        async def _(message):
            raise NotImplementedError()
            # TODO:
            #  Receive message from client
            #  Deserialize message data
            #  Send message to origin service
            #  Wait for answer
            #  Serialize answer
            #  Send data

        return _

    def shutdown(self, message: Message):
        # Remove Service
        raise NotImplementedError()


class ProcessServiceRunner(Service):
    @handler
    async def run_service(self, client, service_class: Type['Service']):
        raise NotImplementedError()
        # TODO:
        #  Create process with ServiceRunner ->
        #    Run Agent
        #    Run ProxyServiceServer for `client` thought Agent


