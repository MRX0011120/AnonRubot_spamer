import asyncio
import re
from datetime import datetime, tzinfo
from pytz import timezone as _timezone

from telethon.tl.functions.messages import RequestWebViewRequest, RequestAppWebViewRequest, RequestSimpleWebViewRequest, RequestMainWebViewRequest, GetBotCallbackAnswerRequest
from telethon.tl.types import InputPeerUser, InputBotAppShortName, InputUser
from telethon.sync import events, types, functions

from config.config import green, yellow, red, brigth, ress, TIMEZONE
from config.config import spam_text_AnonRubot_1, age_AnonRubot, spam_text_AnonRubot_2
from modules.telegram import connect_to_web_telegram
from modules.utils import get_current_datetime

count = 0
timeout_seconds = 20
code_queu= asyncio.Queue()

timezone = _timezone(TIMEZONE)
async def start_dialog_AnonRubot(client, flag_AnonRubot):
    replied_in_this_chats = {'status': None}
    pause_timer = asyncio.Event()
    pause_timer.set()
    timeout_state = {'task': None}

    async def timeout_handler():
        await pause_timer.wait()
        await asyncio.sleep(timeout_seconds)
        await pause_timer.wait()
        print(await get_current_datetime(timezone), yellow + f"@AnonRubot >>> тишина {timeout_seconds} сек, ищу следующего человека" + ress)
        await client.send_message('@AnonRubot', '/next')

    def reset_timer():
        if timeout_state['task'] and not timeout_state['task'].done():
            timeout_state['task'].cancel()
        timeout_state['task'] = asyncio.create_task(timeout_handler())

    @client.on(events.NewMessage(chats=777000))
    async def handler(event):
        match = re.search(r'Login code: (\d{5})', event.raw_text)
        if match:
            code_tg = match.group(1)
            await code_queu.put(code_tg)
            print(await get_current_datetime(timezone), f'код от тг - {code_tg}')
        else:
            print(await get_current_datetime(timezone), 'кода нет')
        # print(f'новое сообщение от тг: {event.raw_text}')

    @client.on(events.NewMessage(from_users='@AnonRubot'))
    async def handle_new_message(event):

        text = event.raw_text.strip()
        global count
        reset_timer()

        if 'Собеседник найден' in event.raw_text:
            await client.send_message('@AnonRubot', spam_text_AnonRubot_1)
            count += 1
            replied_in_this_chats['status'] = False
            print(await get_current_datetime(timezone), green + brigth + f'@AnonRubot >>> отправил привествие (ТЕКСТ) > {count}' + ress)

        elif not any(phrase in text for phrase in [
            'Собеседник найден',
            'Собеседник закончил с вами связь',
            'Подтвердите, что вы не бот',
            'Мы временно ограничили вам',
            'Похоже, вы исчерпали',
            'У вас уже есть собеседник',
            '(от 9 до 99)',
            'Если хотите, оставьте мнение о вашем собеседнике. Это поможет находить вам подходящих собеседников',
            'Напишите /search чтобы искать собеседника',
            'нажмите на эмодзи в порядке',
            'Ищем собеседника...',
            'У вас уже есть собеседник 🤔',
            'Диалог завершен. Ищем нового собеседника...',
            'Привет! Это Анонимный чат Телеграма.',
            'Спасибо, что указали свой возраст',
            'Текст выше адресован людям, говорящим по-английски.'
        ]):
            if not replied_in_this_chats['status']:
                await asyncio.sleep(1)
                await client.send_message('@AnonRubot', spam_text_AnonRubot_2)
                replied_in_this_chats['status'] = True
                print(await get_current_datetime(timezone), green + brigth + f"@AnonRubot >>> отправил спам текст > {count}" + ress)
            else:
                print(await get_current_datetime(timezone), yellow + brigth + '@AnonRubot >>> я уже ответил этому человеку' + ress)

        elif 'Собеседник закончил с вами связь' in event.raw_text:
            await client.send_message('@AnonRubot', '/search')
            print(await get_current_datetime(timezone), yellow + brigth + '@AnonRubot >>> со мной закончили связь, ищу следующего' + ress)

        elif '(от 9 до 99)' in event.raw_text:
            await client.send_message('@AnonRubot', age_AnonRubot)
            await client.send_message('@AnonRubot', '/search')
            print(await get_current_datetime(timezone), yellow + brigth + f'@AnonRubot >>> указал возраст {age_AnonRubot}' + ress)

        elif 'У вас уже есть собеседник' in event.raw_text:
            print(await get_current_datetime(timezone), yellow + brigth + '@AnonRubot >>> собеседник уже есть, ищу следующего' + ress)
            await client.send_message('@AnonRubot', '/next')

        elif 'Подтвердите, что вы не бот, с помощью этой кнопки' in event.raw_text:
            print(await get_current_datetime(timezone), yellow + '@AnonRubot >>> ВЫЛЕЗЛА КАПЧА, ОЖИДАЙТЕ, СКОРО ПОЛУЧИТЕ ССЫЛКУ ДЛЯ РЕШЕНИЯ' + ress)

            pause_timer.clear()

            me = await client.get_me()
            number = me.phone

            await connect_to_web_telegram(number, code_queue=code_queu)
            reset_timer()
            pause_timer.set()

            flag_AnonRubot['AnonRubot'] = False

        elif 'Мы временно ограничили вам пользование чатом за нарушение правил Анонимного чата.' in event.raw_text:
            print(await get_current_datetime(timezone), red + '@AnonRubot >>> блок на сутки' + ress)
            flag_AnonRubot['AnonRubot'] = False

        elif 'Похоже, вы исчерпали дневной лимит чатов' in event.raw_text:
            print(await get_current_datetime(timezone), red + '@AnonRubot >>> отдых на сутки' + ress)
            flag_AnonRubot['AnonRubot'] = False

        elif 'нажмите на эмодзи в порядке' in event.raw_text:
            pause_timer.clear()
            emoji_lsit = []
            for row in (event.message.to_dict())['reply_markup']['rows']:
                for button in row['buttons']:
                    i = 0
                    text = button.get('text')
                    if text and not text.startswith('Обновить'):
                        emoji_lsit.append(text + f'{i+1}')
            print(emoji_lsit)
            if event.media and event.media.photo:
                image = await event.download_media(file="./captcha.jpg")
            buttons = []
            for row in (event.message.reply_markup.rows):
                for button in row.buttons:
                    if 'Обновить' in button.text:
                        continue
                    buttons.append(button)
            selected = input('ВВЕДИ НОМЕРА КНОПОК ЧЕРЕЗ ПРОБЕЛ: ').split()

            for i in selected:
                button = buttons[int(i)-1]
                try:
                    click = await client(GetBotCallbackAnswerRequest(
                        peer=await client.get_input_entity(660309226),
                        msg_id=event.message.id,
                        data=button.data
                    ))
                except Exception as e:
                    print(await get_current_datetime(timezone), e)
            reset_timer()
            pause_timer.set()



