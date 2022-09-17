import os
import redis
from functools import update_wrapper

SEP_REDIS_PASSWORD = os.environ.get('SEP_REDIS_PASSWORD')
SEP_REDIS_HOST = os.getenv('SEP_REDIS_HOST')
SEP_REDIS_PORT = os.getenv('SEP_REDIS_PORT')

pool = redis.ConnectionPool(host = SEP_REDIS_HOST, \
            port = SEP_REDIS_PORT, password = SEP_REDIS_PASSWORD)

def singleton(fn):
    name = fn.__name__
    def wrapper(*args, **kw):
        if name not in singleton.__dict__:
            ret = fn(*args, **kw)
            singleton.__dict__[name] = ret
            return ret
        else:
            return singleton.__dict__[name]
    return update_wrapper(wrapper, fn)

@singleton
def get_redis_client():
    client = redis.Redis(connection_pool=pool, charset="utf-8", decode_responses=True)
    return client
