import asyncio
import sys

from service.runner import ServiceRunner, RunService
import vk_api


async def main():
    asyncio.create_task(ServiceRunner().run())

    klass = ServiceRunner.search(sys.argv[1])

    task = await ServiceRunner.send_task(
        RunService(
            klass, sys.argv[1:]
        )
    )

    print("Task result:")
    print(await task.result())


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
