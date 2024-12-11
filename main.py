from aiohttp import web
from aiohttp.web import HTTPNotFound, HTTPConflict
from models import init_orm, close_orm, Session, Post
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

app = web.Application()


async def get_post_by_id(session: AsyncSession, post_id):
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPNotFound(text='Post is None')
    return post


async def create_user(session: AsyncSession, post: Post):
    try:
        session.add(post)
        await session.commit()
    except IntegrityError:
        raise HTTPConflict(text='Post already exists')


async def context_orm(app: web.Application):
    print('Start programm')
    await init_orm()
    yield
    await close_orm()
    print('Finish programm')


@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        print('Before request')
        request.session = session
        result = await handler(request)
        print('After request')
        return result


app.cleanup_ctx.append(context_orm)
app.middlewares.append(session_middleware)


class PostView(web.View):

    @property
    def post_id(self):
        return int(self.request.match_info['post_id'])
    async def get(self):
        post = await get_post_by_id(self.request.session, self.post_id)
        return web.json_response(post.dict)

    async def post(self):
        json_data = await self.request.json()
        post = Post(**json_data)
        await create_user(self.request.session, post)
        return web.json_response(post.post_id)

    async def patch(self):
        json_data = await self.request.json()
        post = await get_post_by_id(self.request.session, self.post_id)
        for key, value in json_data.items():
            setattr(post, key, value)
        await create_user(self.request.session, post)
        return web.json_response(post.post_id)

    async def delete(self):
        post = await get_post_by_id(self.request.session, self.post_id)
        await self.request.session.delete(post)
        await self.request.session.commit()
        return web.json_response({'status': 'deleted'})


app.add_routes([
    web.get('/post/{post_id:[0-9]+}', PostView),
    web.patch('/post/{post_id:[0-9]+}', PostView),
    web.delete('/post/{post_id:[0-9]+}', PostView),
    web.post('/post', PostView)
])

web.run_app(app)
