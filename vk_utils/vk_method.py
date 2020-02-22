from service import Message, handler
from test.test import TestedService
from vk_utils.registrate import VkSettings
from vk_utils.requests_service import RequestService
from vk_utils.settings import VkSettingsData


class DoVkMethod(Message):
    def __init__(self, method: str, **params):
        super().__init__()
        self.method = method
        self.params = params


class VkMethod(TestedService):
    def __init__(self, message: Message):
        super().__init__(message)
        self.settings: VkSettingsData
        self.additional_params: dict

    async def warm_up(self):
        self.settings = await VkSettings.settings()
        self.additional_params = {
            'access_token': self.settings.token,
            'lang': 'ru',
            'v': "5.103"
        }

    @handler(DoVkMethod)
    async def call_method(self, method, **params):
        return await RequestService.get_request(
            url=f"{self.settings.api_host}{method}",
            data={**params, **self.additional_params}
        )

    async def test_vk_user_get(self):
        response = await self.call_method("users.get", user_ids=210700286)
        answer = response['response'][0]
        assert answer['id'] == 210700286
        assert answer['first_name'] == 'Lindsey'
