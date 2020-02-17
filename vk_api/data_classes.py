# TODO: Dataclass with load from global settings
from .consts import VkPermissions


class VkSettings:
    scope = VkPermissions.FRIENDS | VkPermissions.GROUPS | VkPermissions.OFFLINE | VkPermissions.WALL
    display = "page"
    api_version = "5.103"


class VkSecret:
    def __init__(self, raw_data):
        # TODO: Json loader
        self.client_id = raw_data['client_id']
