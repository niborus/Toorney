from ToorneyBot import ToorneyBot
from aiohttp import web
from urllib.parse import quote
import aiohttp
import jwt
from secrets import token_urlsafe
from config.SECRETS import ToornamentLogin
from customFunctions.discord_oauth2 import generate_discord_oauth2_link, exchange_code
from datetime import datetime, timedelta


async def get_discord_id(bearer_token):
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://discord.com/api/v6/users/@me', headers=headers) as r:
            r.raise_for_status()
            json = await r.json()
            return int(json['id'])


def generate_toornament_oauth2_link(scope: list, state: str) -> str:
    link = 'https://account.toornament.com/oauth2/authorize?' \
           'response_type=code&' \
           'client_id={client_id}&' \
           'redirect_uri={redirect_uri}&' \
           'scope={scope}&' \
           'state={state}'

    return link.format(
        client_id = ToornamentLogin.client_id,
        redirect_uri = quote(ToornamentLogin.callback_url, safe = ''),
        scope = quote(' '.join(scope), safe = ''),
        state = quote(state, safe = ''),
    )


def setup(bot: ToorneyBot):

    @bot.web_api.routes.get('/toorney/start')
    async def start(request):

        link = generate_discord_oauth2_link(
            scope = ['identify'],
            redirect_uri = 'http://localhost:8083/toorney/callback/discord',
            state = token_urlsafe()
        )

        return web.Response(
            status = 200,
            content_type = 'text/html',
            body = '<a href="{0}">{0}</a>'.format(link)
        )

    @bot.web_api.routes.get('/toorney/callback/discord')
    async def callback_discord(request: web.Request):
        code = request.query.get('code')
        discord_token = await exchange_code(
            code,
            redirect_uri = 'http://localhost:8083/toorney/callback/discord',
            scope = ['identify']
        )
        discord_id = await get_discord_id(discord_token['access_token'])
        state = jwt.encode({
            "exp": datetime.utcnow() + timedelta(hours = 1),
            "did": discord_id,  # Discord ID
        }, bot.short_term_hs256_key)
        link = generate_toornament_oauth2_link(['user:info'], state)
        return web.Response(
            status = 200,
            content_type = 'text/html',
            body = '<a href="{0}">{0}</a>'.format(link)
        )

    @bot.web_api.routes.get('/toorney/callback/toornament')
    async def callback_toornament(request: web.Request):

        state = request.query.get('state')
        discord_id = jwt.decode(state, bot.short_term_hs256_key, algorithms = ['HS256']).get('did')

        url = 'https://api.toornament.com/oauth/v2/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': ToornamentLogin.client_id,
            'client_secret': ToornamentLogin.client_secret,
            'redirect_uri': ToornamentLogin.callback_url,
            'code': request.query.get('code'),
        }
        headers = {
            'X-Api-Key': ToornamentLogin.api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data = data, headers = headers) as r:
                json = await r.json()
                token = json.get('access_token')

        url = "https://api.toornament.com/account/v2/me/info"
        headers['Authorization'] = f'Bearer {token}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url, data = data, headers = headers) as r:
                json = await r.json()
                toornament_id = json.get('id')

        return web.json_response({"discord_id": discord_id, "toornament_id": toornament_id})
