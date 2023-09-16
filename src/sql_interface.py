from prisma import Prisma
import deadlines as dl


async def many_deadlines(**query):
    client = Prisma()
    await client.connect()
    result = await client.deadline.find_many(**query)
    await client.disconnect()
    return [dl.Deadline(x) for x in result]


# async def create_deadline(**query):
#     client = Prisma()
#     await client.connect()
#     await client.deadline.create(**query)
#     await client.disconnect


# async def delete_deadline(**query):
#     client = Prisma()
#     await client.connect()
#     await client.deadline.delete(**query)
#     await client.disconnect
