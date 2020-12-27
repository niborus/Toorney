import aiohttp
from discord import Webhook, AsyncWebhookAdapter, AllowedMentions


async def execute_webhook_with_edit(webhook_id, token, content=None, *, wait=False, username=None, avatar_url=None,
                                    tts=False,
                                    file=None, files=None, embed=None, embeds=None, allowed_mentions=None,
                                    avatar_bytes=None):
    if allowed_mentions is None:
        allowed_mentions = AllowedMentions(everyone = False, users = False, roles = False)
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.partial(webhook_id, token, adapter = AsyncWebhookAdapter(session))
        if username:
            await webhook.edit(name = username)
        if avatar_bytes:
            await webhook.edit(avatar = avatar_bytes)
        await webhook.send(content = content, wait = wait, username = username, avatar_url = avatar_url, tts = tts,
                           file = file, files = files, embed = embed, embeds = embeds,
                           allowed_mentions = allowed_mentions)


async def _execute_webhook(*, url=None, webhook_id=None, token=None, allowed_mentions=None, **kwargs):
    if allowed_mentions is None:
        allowed_mentions = AllowedMentions(everyone = False, users = False, roles = False)
    async with aiohttp.ClientSession() as session:
        if webhook_id:
            webhook = Webhook.partial(webhook_id, token, adapter = AsyncWebhookAdapter(session))
        else:
            webhook = Webhook.from_url(url, adapter = AsyncWebhookAdapter(session))
        await webhook.send(allowed_mentions = allowed_mentions, **kwargs)


async def execute_webhook_by_id(webhook_id, token, content=None, *, wait=False, username=None, avatar_url=None,
                                tts=False, file=None, files=None, embed=None, embeds=None, allowed_mentions=None):
    await _execute_webhook(webhook_id = webhook_id, token = token, content = content, wait = wait, username = username,
                           avatar_url = avatar_url, tts = tts, file = file, files = files, embed = embed,
                           embeds = embeds, allowed_mentions = allowed_mentions)


async def execute_webhook_by_url(url, content=None, *, wait=False, username=None, avatar_url=None,
                                 tts=False, file=None, files=None, embed=None, embeds=None, allowed_mentions=None):
    await _execute_webhook(url = url, content = content, wait = wait, username = username,
                           avatar_url = avatar_url, tts = tts, file = file, files = files, embed = embed,
                           embeds = embeds, allowed_mentions = allowed_mentions)
