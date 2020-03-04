from test import TestedService
from vk_utils.requests_service import RequestService


class TestRequestService(TestedService):
    async def test_youtrack_is_alive(self):
        answer = await RequestService.get_request("https://youtrack.abstractly.org/api")
        assert 'error' in answer
        assert 'error_description' in answer
