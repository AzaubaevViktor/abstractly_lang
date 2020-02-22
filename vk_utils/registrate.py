import webbrowser

from service import Service, Message, handler
from vk_utils.redirect_server import RedirectServer
from vk_utils.settings import VkSettingsData


class VkRegistration(Service):
    def __init__(self, message: Message):
        super().__init__(message)
        self.redirect_address: str = None

    async def warm_up(self):
        self.redirect_address = await RedirectServer.get_address()

    @handler
    async def do_register(self, client_id):
        url = "https://oauth.vk.com/authorize" \
              f"?client_id={client_id}" \
              "&display=page" \
              f"&redirect_uri={self.redirect_address}" \
              "&scope=friends,wall,offline,groups" \
              "&response_type=token" \
              "&v=5.103"

        webbrowser.open_new(url)

        path: dict = await RedirectServer.get_data()
        return path


class VkSettings(Service):
    @handler
    async def settings(self) -> VkSettingsData:
        settings = await VkSettingsData.load("settings.yml")

        if not settings.token:
            data = await VkRegistration.do_register(client_id=settings.client_id)
            settings.token = data['access_token']
            settings.user_id = data['user_id']
            await settings.store("settings.yml")

        return settings
