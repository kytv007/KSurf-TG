from asyncio import get_event_loop, sleep as asleep, gather
from traceback import format_exc

from aiohttp import web
from pyrogram import idle
from os import environ
from bot import __version__, LOGGER
from bot.config import Telegram
from bot.server import web_server
from bot.telegram import StreamBot, UserBot
from bot.telegram.clients import initialize_clients

loop = get_event_loop()

async def start_services():
    LOGGER.info(f'Initializing Surf-TG v-{__version__}')
    await asleep(1.2)

    await gather(StreamBot.start(), UserBot.start())
    StreamBot.username = StreamBot.me.username
    LOGGER.info(f"Bot Client : {StreamBot.username}")
    UserBot.username = UserBot.me.username or UserBot.me.first_name or UserBot.me.id
    LOGGER.info(f"User Client : {UserBot.username}")

    await asleep(1.2)
    LOGGER.info("Initializing Multi Clients")
    await initialize_clients()
    
    await asleep(2)
    LOGGER.info('Initalizing Surf Web Server..')
    server = web.AppRunner(await web_server())
    LOGGER.info("Server CleanUp!")
    await server.cleanup()

    await asleep(2)
    LOGGER.info("Server Setup Started !")

    await server.setup()
    port = int(environ.get("PORT", 8080))
    await web.TCPSite(server, '0.0.0.0', port).start()
    await asleep(2)
    
    await idle()


async def stop_clients():
    await gather(StreamBot.stop(), UserBot.stop())

if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        LOGGER.info('Service Stopping...')
    except Exception as err:
        LOGGER.error(format_exc())
    finally:
        loop.run_until_complete(stop_clients())
        loop.stop()
