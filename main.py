import asyncio
import sys
from typing import Sequence

from log import Log
from service import  EntryPoint

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


async def main(cmd):
    entry_point = EntryPoint({
        cmd.service_name: [(cmd.message_name, cmd.kwargs)]
    })

    await entry_point.warm_up()
    await entry_point.run()


if __name__ == '__main__':
    logger = Log("Main")

    logger.info("Parse cmd")

    cmd = CmdParser(sys.argv)

    asyncio.run(main(cmd), debug=True)
