import json
import random

import redis
from redis import StrictRedis


class CookiePool:
    redis_client: StrictRedis

    def __init__(self, host: str, port: int, db: int, password: str):
        self.redis_client = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            password=password
        )
        self.redis_client.ping()

    def save_cookie(self, website: str, user_id: str, cookies: list[dict]):
        self.redis_client.hset(f"{website}_cookie", user_id, json.dumps(cookies))

    def _get_cookies(self, website: str) -> dict:
        sets = self.redis_client.hgetall(f"{website}_cookie")
        result = {}
        for k, v in sets.items():
            result[k.decode()] = json.loads(v.decode())
        return result

    def get_rand_cookie(self, website: str) -> list[dict]:
        sets = self._get_cookies(website)
        l = list(sets.values())
        if len(l) == 0:
            return []
        cookie_ = random.choice(l)
        return cookie_

    def del_cookie(self, website: str, user_id: str):
        self.redis_client.hdel(f"{website}_cookie", [user_id])
