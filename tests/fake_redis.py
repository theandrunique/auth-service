class FakeRedis:
    def __init__(self):
        self.data = {}

    async def set(self, key, value, **args):
        self.data[key] = value

    async def get(self, key):
        return self.data.get(key)

    async def delete(self, key):
        del self.data[key]
