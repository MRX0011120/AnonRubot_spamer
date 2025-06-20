import asyncio
import os

from telethon.tl.functions.contacts import UnblockRequest
from art import text2art
from chats.AnonRubot import start_dialog_AnonRubot
from modules.telegram import connect_to_telegram
from config.config import red, ress

sessions = os.listdir('./sessions')

print(red + '''Автор - https://t.me/mrx_soft_coder\nКанал автора с софтами - https://t.me/mrx_soft\nLolz автора - https://zelenka.guru/members/5331652/''' + ress)
art = text2art("MRX-SOFT", space=2)
print(red + art + ress)
async def start_spam(session_path):

    client = await connect_to_telegram(session_path)

    if client is None:
        return
    # else:
    #     await start_dialog_AnonRubot(client, chat_access_state)
    flag_AnonRubot = {'AnonRubot': True}
    # async with client:
    try:
        # await client.send_message(777000, '/start')
        await client(UnblockRequest('@AnonRubot'))
        await client.send_message('@AnonRubot', '/next')
        await start_dialog_AnonRubot(client, flag_AnonRubot)

        while flag_AnonRubot['AnonRubot']:
            await asyncio.sleep(2)
    except Exception as e:
        print(f'В {session_path} - ошибка - {e}')

    finally:
        await client.disconnect()
        print(f'{session_path} - СЕССИЯ ЗАВЕРШЕНА')

    # if not chat_access_state['AnonRubot_flag']:
    #     await client.disconnect()

async def main():
    for session in sessions:
        session_path = os.path.join('./sessions', session)
        await start_spam(session_path)

if __name__ == '__main__':
    asyncio.run(main())