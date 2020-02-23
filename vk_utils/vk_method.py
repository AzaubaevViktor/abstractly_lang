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


def wait_timing(exceptions):
    pass


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
        result = await RequestService.get_request(url=f"{self.settings.api_host}{method}",
                                                  data={**params, **self.additional_params})
        assert 'response' in result, result
        response = result['response']
        if isinstance(response, list) and len(response) == 1:
            return response[0]
        else:
            return response

    @handler
    async def get_profile_info(self):
        return await self.call_method("account.getProfileInfo")

    @handler
    async def user_friends(self,
                           user: int,
                           count: int = None
                           ):
        friends = []
        if count is not None:
            raise NotImplementedError()

        while True:
            answer = await self.call_method(
                "friends.get",
                user_id=user,
                order='name',
                count=5000,
                offset=len(friends),
                name_case="nom"
            )

            items = answer['items']
            friends.extend(items)

            assert len(items) != 0

            if answer['count'] <= len(friends):
                break

        return friends

    @handler
    async def user_groups(self, user: int):
        groups = []

        while True:
            answer = await self.call_method(
                "groups.get",
                user_id=user,
                extended=0,
                count=1000,
                offset=0
            )

            items = answer['items']
            groups.extend(items)

            assert len(items) != 0

            if answer['count'] <= len(groups):
                break

        return groups

    @handler
    async def users_info(self, *users):
        assert len(users) <= 1000, "Not implemented yet. Implement if you want..."
        return await self.call_method(
            "users.get",
            user_ids=",".join(map(str, set(users))),
            fields="first_name,last_name,deactivated,verified",
            name_case="nom"
        )

    async def test_vk_user_get(self):
        answer = await self.call_method("users.get", user_ids=210700286)

        assert answer['id'] == 210700286
        assert answer['first_name'] == 'Lindsey'

    async def test_users_info(self):
        answer = await self.users_info(210700286, 210700286, 169845376)

        assert len(answer) == 2

        for item in answer:
            assert 'id' in item, item.keys()
            assert 'first_name' in item, item.keys()
            assert 'last_name' in item, item.keys()

    async def test_user_friends9000(self):
        friends = await self.user_friends(169845376)
        assert len(friends) > 6000, len(friends)