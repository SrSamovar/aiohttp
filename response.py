import aiohttp
import asyncio


async def main():
    session = aiohttp.ClientSession()

    response = await session.post(
        'http://127.0.0.1:8080/post',
        json={
            'title': 'title_2',
            'description': 'description_2',
            'author': 'author_2'
        },
        headers={'token': '1234'}
                                  )

    # response = await session.get('http://127.0.0.1:8080/post/1')
    print(response.status)
    print(await response.text())

    await session.close()

asyncio.run(main())
