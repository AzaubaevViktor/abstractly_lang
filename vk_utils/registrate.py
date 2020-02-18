import webbrowser

from service import Service, Message
from service.error import UnknownMessageType
from vk_utils.redirect_server import RedirectServer, GetAddress, GetPath
from vk_utils.settings import VkSettingsData


class DoRegister(Message):
    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id


class GetSettings(Message):
    pass


class VkRegistration(Service):
    def __init__(self, message: Message):
        super().__init__(message)
        self.redirect_address: str = None

    async def warm_up(self):
        self.redirect_address = await RedirectServer.get(GetAddress())

    async def process(self, message: Message):
        if isinstance(message, DoRegister):
            url = "https://oauth.vk.com/authorize" \
                  f"?client_id={message.client_id}" \
                  "&display=page" \
                  f"&redirect_uri={self.redirect_address}" \
                  "&scope=friends,wall,offline,groups" \
                  "&response_type=token" \
                  "&v=5.103"

            webbrowser.open_new(url)

            path = await RedirectServer.get(GetPath())
            return path

        raise UnknownMessageType(self, message)


class VkSettings(Service):
    async def process(self, message: Message):
        if isinstance(message, GetSettings):
            settings = await VkSettingsData.load("settings.yml")

            if not settings.token:
                settings.token = await self.get(DoRegister(settings.client_id))
                await settings.store("settings.yml")

            return settings

        raise UnknownMessageType(self, message)

