import deadlines as dl
import requests


async def many_deadlines(programme: str):
    result = requests.get("https://deadline-web.vercel.app/api/" + programme)
    json = result.json()
    deadlines = []
    for course in json['courses']:
        for deadline in course['deadlines']:
            deadlines.append(deadline)

    print(deadlines)

    return [dl.Deadline(x) for x in deadlines]
