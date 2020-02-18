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

            path: str = await RedirectServer.get(GetPath())
            return dict(item.split('=') for item in path.split("&"))

        raise UnknownMessageType(self, message)


class VkSettings(Service):
    async def process(self, message: Message):
        if isinstance(message, GetSettings):
            settings = await VkSettingsData.load("settings.yml")

            if not settings.token:
                data = await VkRegistration.get(DoRegister(settings.client_id))
                settings.token = data['access_token']
                settings.user_id = data['user_id']
                await settings.store("settings.yml")

            return settings

        raise UnknownMessageType(self, message)

    @classmethod
    async def settings(cls) -> VkSettingsData:
        return await cls.get(GetSettings())
