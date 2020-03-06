from random import randint
from typing import Optional


class TokenT(int):
    pass


class _ClientInfo:
    def __init__(self, sid):
        self.token = None
        self.sid = sid


class _Clients:
    def __init__(self):
        self.clients = []
        self._tokens = []

        self._by_sid_cache = {}

    def new_token(self) -> TokenT:
        token = randint(0, 100000000)
        self._tokens.append(token)
        return TokenT(token)

    def connected(self, sid: str) -> _ClientInfo:
        client = _ClientInfo(sid)
        self.clients.append(client)
        return client

    def apply_token(self, sid: str, token: TokenT) -> _ClientInfo:
        client = self.by_sid(sid)
        assert token in self._tokens
        del self._tokens[token]
        client.token = token
        return client

    def _search_by_attr(self, attr_name, value):
        for client in self.clients:
            if getattr(client, attr_name) == value:
                return client

    def by_sid(self, sid: str) -> Optional[_ClientInfo]:
        if sid not in self._by_sid_cache:
            client = self._search_by_attr('sid', sid)
            if client:
                self._by_sid_cache[sid] = client

        return self._by_sid_cache.get(sid)

    def drop(self, client: '_ClientInfo'):
        del self._by_sid_cache[client.sid]


