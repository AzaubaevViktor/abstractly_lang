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
    async def get_friends(self,
                          user: int,
                          count: int = None
                          ):
        friends = []
        if count is not None:
            raise NotImplementedError()

        answer = await self.call_method(
            "friends.get",
            user_id=user,
            order='name',
            count=5000,
            offset=len(friends),
            fields="nickname,domain,sex,bdate,city,country,timezone,"
                   "photo_50,photo_100,photo_200_orig,has_mobile,contacts,"
                   "education,online,relation,last_seen,status,"
                   "can_write_private_message,can_see_all_posts,can_post,universities",
            name_case="nom"
        )

        items = answer['items']
        friends.extend(items)

        if answer['count'] == 5000:
            answer = await self.call_method(
                "friends.get",
                user_id=user,
                order='name',
                count=5000,
                offset=5000,
                name_case="nom"
            )

            friends.extend(answer['items'])

        return friends

    async def test_vk_user_get(self):
        answer = await self.call_method("users.get", user_ids=210700286)

        assert answer['id'] == 210700286
        assert answer['first_name'] == 'Lindsey'

    async def test_get_friends9000(self):
        friends = await self.get_friends(169845376)
        assert len(friends) > 6000, len(friends)