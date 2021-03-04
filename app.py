'''
    This is a simple async server app, with examples of rest api endpoints, websockets handler and
    template rendering
'''
import os

from aiohttp import web
import aiohttp

import aiohttp_jinja2
import jinja2
from gino.ext.aiohttp import Gino

from models.models import User

# Database Configuration
PG_URL = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    database=os.getenv("DB_DATABASE", "postgres"),
)

#INSTANTIATING WEB APP AND INITIALIZE ANOTHER STUFF
db = Gino()
app = web.Application(middlewares=[db])
db.init_app(app, dict(dsn=PG_URL)) #Initializing db

'''
    We keep sockets stored in app so this memory strategy only works with one worker/instance, not for 
    production usage.
    If you want to use sockets in production it would be better to use PUB/SUB with Redis.
'''
app['websockets'] = []
aiohttp_jinja2.setup(app,
    loader=jinja2.FileSystemLoader('./templates'))

#DEFINING VIEW FUNCTIONS
async def template_rendering(request):
    context = {'author':'Alexis Piña'}
    return aiohttp_jinja2.render_template('home_template.html', 
        request, context)

async def vue_template(request):
    return aiohttp_jinja2.render_template('vue_template.html', request, context={})

async def get_me_data(request):
    data = {
        'name':'Alexis',
        'last_name':'Piña Aquino',
        'phone_number':'5581064181',
        'age':26,
        'company':'Chelita Software',
        'role':'Software Engineer'
    }
    return web.json_response(data)

async def post_comment(request):
    data = await request.post()
    comment = data.get('comment')
    if comment:
        for _ws in request.app['websockets']:
            await _ws.send_str(comment)
        return web.json_response({'success':True})
    return web.json_response({'success':False, 'message':'Comment is empty!'})

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app['websockets'].append(ws)
    print('WS Connection Started - ' + str(len(request.app['websockets'])))

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                for _ws in request.app['websockets']:
                    await _ws.send_str(msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    request.app['websockets'].remove(ws)
    return ws

#ROUTING VIEWS
app.add_routes([
        web.get('/', template_rendering),
        web.get('/me', get_me_data),
        web.post('/send_comment', post_comment),
        web.get('/ws', websocket_handler),
        web.get('/vue', vue_template)
    ])

async def create(app_):
    await db.gino.create_all()

app.on_startup.append(create)

#RUNNING SERVER
if __name__ == '__main__':
    web.run_app(app)