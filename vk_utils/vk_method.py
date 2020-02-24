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
        self.user_fields = ",".join([
            "first_name", "last_name", "deactivated", "verified",
            "sex", "bdate",
            "city",  # TODO: https://vk.com/dev/places.getCityById
            "country",  # TODO: https://vk.com/dev/places.getCountryById
            "home_town",
            "photo_400_orig",
            "online",
            "has_mobile",
            "contacts",
            "education",
            "universities",
            "schools",
            "last_seen",
            "occupation"
        ])

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

    async def _count_offset_wrapper(self, method, *, default_step, count=None, **params):
        all_items = []

        assert default_step is not None, "Set default step!"

        if count is not None:
            raise NotImplementedError()

        while True:
            answer = await self.call_method(
                method, **params,
                count=default_step,
                offset=len(all_items)
            )

            items = answer['items']
            all_items.extend(items)

            assert len(items) != 0

            if answer['count'] <= len(all_items):
                break

        assert answer['count'] == len(all_items)

        return all_items

    @handler
    async def user_friends(self,
                           user: int,
                           count: int = None
                           ):
        return await self._count_offset_wrapper(
            "friends.get",
            user_id=user,
            order='name',
            name_case="nom",
            default_step=5000
        )

    @handler
    async def user_groups(self, user: int):
        return await self._count_offset_wrapper(
            "groups.get",
            user_id=user,
            extended=0,
            default_step=1000,
        )

    @handler
    async def users_info(self, *users):
        assert len(users) <= 1000, "Not implemented yet. Implement if you want..."
        return await self.call_method(
            "users.get",
            user_ids=",".join(map(str, set(users))),
            fields=self.user_fields,
            name_case="nom"
        )

    @handler
    async def wall(self,
                   owner: int):

        return await self._count_offset_wrapper(
            "wall.get",
            owner=owner,
            filter="all",
            extended=0,
            default_step=100
        )

    @handler
    async def wall_post(self,
                        owner: int,
                        post: int):
        return await self._count_offset_wrapper(
            "wall.getComments",
            owner_id=owner,
            post_id=post,
            need_likes=1,
            sort="asc",  # or desc
            preview_length=0,
            extended=0,
            default_step=100
        )

    async def group_users(self, group: int):
        return await self._count_offset_wrapper(
            "groups.getMembers",
            group_id=group,
            sort="id_asc",
            default_step=1000
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
            assert "online" in item, item.keys()

    async def test_user_friends9000(self):
        friends = await self.user_friends(169845376)
        assert len(friends) > 6000, len(friends)

    async def test_wall(self):
        answer = await self.wall(owner=-86529522)
        assert answer
        for post in answer:
            assert "id" in post
            assert "post_type" in post

    async def test_wall_post(self):
        post_id = 3199
        answer = await self.wall_post(
            owner=85635407,
            post=post_id
        )

        assert answer
        for comment in answer:
            assert "id" in comment
            assert comment['post_id'] == post_id

    async def test_group_users(self):
        answer = await self.group_users(group=14444)
        assert len(answer)
