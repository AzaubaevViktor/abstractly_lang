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

    result = await msg.result()
    logger.important(result)


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
