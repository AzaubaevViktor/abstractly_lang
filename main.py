import asyncio
import sys

from log import Log
from service import ServiceRunner, Message, RunService, Service

import test
import vk_utils


async def main():
    logger = Log("Main")

    logger.info("Create ServiceRunner")
    instance = ServiceRunner(Message())
    logger.info("Search klass")
    klass = Service.search(sys.argv[1])

    msg = await ServiceRunner.send(RunService(klass))

    logger.info("Run ServiceRunner")

    asyncio.create_task(instance.run())

    logger.info("Wait while ready")

    if sys.argv[2]:
        msg_klass = Message.search(sys.argv[2])
        msg_args = sys.argv[3:]
        logger.info("Send additional message", klass=msg_klass, args=msg_args)
        logger.important(await klass.get(msg_klass(*msg_args)))

    result = await msg.result()
    logger.important(result)


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
