from random import randint
from typing import Optional, Dict, List

from core import AttributeStorage, Attribute
from service import BaseCommunicator


class TokenT(int):
    pass


class ClientInfo(AttributeStorage):
    sid = Attribute()
    token = Attribute(default=None)
    comm = Attribute(default=None)

class Clients:
    def __init__(self):
        self.clients: List[ClientInfo] = []
        self._tokens: Dict[TokenT, BaseCommunicator] = {}

        self._by_sid_cache = {}

    def new_token(self, communicator: BaseCommunicator) -> TokenT:
        token = randint(0, 100000000)
        self._tokens[token] = communicator
        return TokenT(token)

    def connected(self, sid: str) -> ClientInfo:
        client = ClientInfo(sid=sid)
        self.clients.append(client)
        return client

    def apply_token(self, sid: str, token: TokenT) -> ClientInfo:
        client = self.by_sid(sid)
        assert client

        assert token in self._tokens, (sid, token, self._tokens)
        client.comm = self._tokens[token]
        del self._tokens[token]
        client.token = token
        return client

    def _search_by_attr(self, attr_name, value):
        for client in self.clients:
            if getattr(client, attr_name) == value:
                return client

    def by_sid(self, sid: str) -> Optional[ClientInfo]:
        if sid not in self._by_sid_cache:
            client = self._search_by_attr('sid', sid)
            if client is not None:
                self._by_sid_cache[sid] = client

        return self._by_sid_cache.get(sid)

    def drop(self, client: 'ClientInfo'):
        del self._by_sid_cache[client.sid]


