from ToorneyBot import ToorneyBot
from aiohttp import web
from urllib.parse import quote
from secrets import token_urlsafe
import aiohttp
from config.SECRETS import ToornamentLogin


def setup(bot: ToorneyBot):

    @bot.web_api.routes.get('/')
    async def Test(request):
        return web.Response(status = 200, body = "<h2>Hello World</h2>", content_type = 'text/html')

    @bot.web_api.routes.get('/toornament/start')
    async def start(request):
        return web.Response(
            status = 200,
            content_type = 'text/html',
            body = '<a href="{0}">{0}</a>'.format(
                'https://account.toornament.com/oauth2/authorize?response_type=code&client_id={client_id}&'
                'redirect_uri={redirect_uri}&scope={scope}&state={state}'.format(
                    client_id = ToornamentLogin.client_id,
                    redirect_uri = quote('http://localhost:8083/toornament/callback', safe = ''),
                    scope = quote('user:info', safe = ''),
                    state = token_urlsafe()
                )
            )
        )

    @bot.web_api.routes.get('/toornament/callback')
    async def callback(request: web.Request):
        url = 'https://api.toornament.com/oauth/v2/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': ToornamentLogin.client_id,
            'client_secret': ToornamentLogin.client_secret,
            'redirect_uri': 'http://localhost:8083/toornament/callback',
            'code': request.query.get('code'),
        }
        headers = {
            'X-Api-Key': ToornamentLogin.api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data = data, headers = headers) as r:
                return web.json_response(await r.json())
