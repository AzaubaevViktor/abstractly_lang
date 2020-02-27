import asyncio
import sys
from typing import Sequence

from log import Log
from service import ServiceRunner, Message, Service, RunService

import test
import vk_utils
from service.message import Shutdown


class CmdParser:
    def __init__(self, args):
        self.app_name = args[0]
        self.service_name = None
        self.message_name = None
        self.kwargs = {}

        if len(args) > 1:
            self.service_name = args[1]

        if len(args) > 2:
            self.message_name = args[2]

        if len(args) > 3:
            self.args, self.kwargs = self._parse_args(args[3:])

    def _parse_args(self, params: Sequence):
        args = []
        kwargs = {}
        for item in params:
            if item.startswith("--"):
                k, v = item[2:].split('=')
                kwargs[k] = v
            else:
                raise NotImplementedError(item)

        return args, kwargs


async def main():
    logger = Log("Main")

    logger.info("Parse cmd")

    cmd = CmdParser(sys.argv)

    logger.info("Create ServiceRunner")
    instance = ServiceRunner(Message())
    logger.info("Search service", service=cmd.service_name)
    service_class = Service.search(cmd.service_name)

    Service.main_queue = asyncio.Queue()

    msg = await ServiceRunner.send(RunService(service_class=service_class))

    logger.info("Run ServiceRunner")

    asyncio.create_task(instance.run())

    logger.info("Wait while ready")

    run_msg_result = None

    if cmd.message_name:
        msg_klass = Message.search(cmd.message_name)

        logger.info("Send additional message",
                    msg=msg_klass,
                    kwargs=cmd.kwargs)

        run_msg_result = await service_class.get(msg_klass(**cmd.kwargs))

        logger.info("Shutdown service")

        await service_class.send(Shutdown(cause="Finished main"))

    run_result = await msg.result()

    await ServiceRunner.get(Shutdown(cause="Finished main"))

    if run_msg_result:
        logger.important(run_msg_result)
    else:
        logger.important(run_result)


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
