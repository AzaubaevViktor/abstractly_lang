import aiofiles
import yaml


class VkSettingsData:
    def __init__(self, raw_data: dict):
        self.client_id = raw_data['vk']['client_id']
        self.token = raw_data['vk'].get('token', None)
        self.user_id = raw_data['vk'].get('user_id', None)

    def __iter__(self):
        yield 'vk', {
            'client_id': self.client_id,
            'token': self.token,
            'user_id': self.user_id
        }

    @classmethod
    async def load(self, file_name) -> "VkSettingsData":
        async with aiofiles.open(file_name, mode='rt') as f:
            contents = await f.read()
        return VkSettingsData(yaml.safe_load(contents))

    async def store(self, file_name):
        async with aiofiles.open(file_name, mode='wt') as f:
            await f.write(yaml.safe_dump(dict(self)))
