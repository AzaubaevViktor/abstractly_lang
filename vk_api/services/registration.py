import json
import webbrowser

import aiofiles as aiofiles

from service.base import Service
from vk_api.data_classes import VkSecret, VkSettings


class VkRedirectWebServer(Service):
    async def warm_up(self):
        pass


class VkRegistration(Service):
    FILE_NAME = "secret.json"

    async def _load_secret(self) -> VkSecret:
        self.logger.info("Get secret data", file_name=self.FILE_NAME)
        async with aiofiles.open(self.FILE_NAME, mode='r') as f:
            contents = await f.read()
        data = json.loads(contents)

        return VkSecret(data)

    async def _start_redirect_server(self) -> str:
        self.logger.info("Starting web server")
        # TODO: class URL
        return "https://oauth.vk.com/blank.html"

    async def warm_up(self):
        secret = await self._load_secret()
        redirect_uri = await self._start_redirect_server()

        link = "https://oauth.vk.com/authorize?" \
               f"client_id={secret.client_id}&" \
               f"scope={VkSettings.scope}&" \
               f"redirect_uri={redirect_uri}&" \
               f"display={VkSettings.display}&" \
               f"v={VkSettings.api_version}&" \
               "response_type=token"

        self.logger.info("Open browser")
        webbrowser.open_new(link)
