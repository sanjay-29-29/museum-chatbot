from prisma import Prisma

class PrismaClient:
    _instance = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = Prisma()
            await cls._instance.connect()
        return cls._instance