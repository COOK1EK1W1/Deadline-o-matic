from prisma import Prisma
import deadlines as dl


async def many_deadlines(**query):
    client = Prisma()
    await client.connect()
    result = await client.deadline.find_many(**query)
    await client.disconnect()
    return [dl.Deadline(x) for x in result]
