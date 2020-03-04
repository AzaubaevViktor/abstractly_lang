from test import TestedService
from vk_utils import VkMethod


class TestVkMethod(TestedService):
    async def test_vk_user_get(self):
        answer = await VkMethod.call_method("users.get", user_ids=210700286)

        assert answer['id'] == 210700286
        assert answer['first_name'] == 'Lindsey'

    async def test_users_info(self):
        answer = await VkMethod.users_info(210700286, 210700286, 169845376)

        assert len(answer) == 2

        for item in answer:
            assert 'id' in item, item.keys()
            assert 'first_name' in item, item.keys()
            assert 'last_name' in item, item.keys()
            assert "online" in item, item.keys()

    async def test_user_friends9000(self):
        friends = await VkMethod.user_friends(169845376)
        assert len(friends) > 6000, len(friends)

    async def test_wall(self):
        answer = await VkMethod.wall(owner=-86529522)
        assert answer
        for post in answer:
            assert "id" in post
            assert "post_type" in post

    async def test_wall_post(self):
        post_id = 3199
        answer = await VkMethod.wall_post(
            owner=85635407,
            post=post_id
        )

        assert answer
        for comment in answer:
            assert "id" in comment
            assert comment['post_id'] == post_id

    async def test_group_users(self):
        answer = await VkMethod.group_users(group=14444)
        assert len(answer)