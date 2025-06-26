import asyncio.constants
import python_socks

from pytz import timezone as _timezone
from playwright.async_api import async_playwright
from telethon.sync import TelegramClient
from config.config import PROXY, API_ID, API_HASH, TIMEZONE, green, yellow, red, ress
from modules.utils import get_current_datetime

timezone = _timezone(TIMEZONE)

async def connect_to_telegram(session_path, api_id = API_ID, api_hash = API_HASH):
    try:
        proxy = {
            "proxy_type": python_socks.ProxyType.SOCKS5,
            "addr": PROXY['host'],
            "port": PROXY['port'],
            "username": PROXY['username'],
            "password": PROXY['password'],
            "rdns": True
        }
        client = TelegramClient(session_path, api_id, api_hash, proxy=proxy)
        await client.connect()
        if not await client.is_user_authorized():
            print(await get_current_datetime(timezone) ,red + f"{session_path} - НЕВАЛИД" + ress)
            return None
        else:
            print(await get_current_datetime(timezone), red + f"{session_path} - ВЗЯЛ СЕССИЮ В РАБОТУ" + ress)
            return client
    except Exception as e:
        print(await get_current_datetime(timezone), red + "ПРОКСИ НЕ РАБОТАЕТ" + ress)

async def connect_to_web_telegram(numbers_from_session, code_tg=None, code_queue=None):
    async with async_playwright() as p:
        proxy_socks = {
            "server": f"http://{PROXY['host']}:{PROXY['port']}",
            "username" : f"{PROXY['username']}",
            "password": f"{PROXY['password']}"
        }
        browser = await p.firefox.launch(
            headless=True,
            proxy=proxy_socks
        )
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://web.telegram.org/a/", wait_until="domcontentloaded", timeout=120_000)
        #нажатие на поле с "войти по номеру"
        try:
            login = await page.wait_for_selector("text=LOG IN BY PHONE NUMBER", timeout=120_000)
            await login.click()
        except:
            print(get_current_datetime(timezone), red + f"ПЕРЕЗАПУСТИ СОФТ, КОД ОШИБКИ 101 (СМОТРЕТЬ ТУТ >>> https://github.com/MRX0011120/AnonRubot_spamer)")
        #нажатие на поле с номером
        try:
            number_input = await page.wait_for_selector("input#sign-in-phone-number", timeout=30000)
            await number_input.click()
        except:
            print(get_current_datetime(timezone), red + f"ПЕРЕЗАПУСТИ СОФТ, КОД ОШИБКИК 102 (СМОТРЕТЬ ТУТ >>> https://github.com/MRX0011120/AnonRubot_spamer")


        #выделяем весь текст
        await page.keyboard.press('Control+A')
        #удаляем весь текст
        await page.keyboard.press('Backspace')
        # print('удалил весь текст')

        #заполняем поле с номером
        await number_input.fill(f"+{numbers_from_session}")
        await page.keyboard.press('Enter')

        #ждем поле для ввода кода
        try:
            await page.wait_for_selector("input#sign-in-code", timeout=30000)
            code_input = page.locator("input#sign-in-code")
            await code_input.wait_for(timeout=30000)
            await code_input.click()
        except:
            print(get_current_datetime(timezone), )
        if code_tg is None and code_queue is not None:
            try:
                print('TG - ЖДУ КОД ОТ TG')
                code_tg = await asyncio.wait_for(code_queue.get(), timeout=60)
                print(f'TG - КОД ОТ TG ПОЛУЧЕН: {code_tg}')
            except asyncio.TimeoutError:
                print('TG - КОД ОТ TG ЗА 60 СЕКУНД НЕ БЫЛ ПОЛУЧЕН :(')
                return
        elif code_tg is None:
            print('TG - КОД ОТ TG ВООБЩЕ НЕ ПРИШЕЛ')
            return
        print(code_tg)
        await code_input.fill(code_tg)
        print("✅TG - КОД БЫЛ УСПЕШНО ВВЕДЕН")

        entered_code = await code_input.input_value()

        await page.keyboard.press('Enter')

        # нажимаем на чат с анонботом
        await page.wait_for_selector('a.ListItem-button[href="#660309226"]', timeout=30000)
        await page.click('a.ListItem-button[href="#660309226"]')

        # тут врооде получить все сообщения в чате
        await page.wait_for_selector('div.message-date-group')
        messages = await page.query_selector_all('div.message-date-group')

        try:
            button = await page.wait_for_selector('button[aria-label="Go to bottom"]', timeout=2000)
            await button.click()
        except:
            print('кнопки в низ не было')

        if messages:
            last_message = messages[-1]
            # await last_message.wait_for_selector('div.Message.message-list-item.first-in-group.allow-selection.last-in-group.last-in-list.has-inline-buttons.shown.open', timeout=10000)
            message_div = await last_message.query_selector(
                'div.Message.message-list-item.first-in-group.allow-selection.last-in-group.last-in-list.has-inline-buttons.shown.open')

            if message_div:
                await message_div.wait_for_selector('button:has-text("Я не бот")')
                button = await message_div.query_selector('button:has-text("Я не бот")')

                if button:
                    await button.click()
                    await page.wait_for_selector('button.Button.confirm-dialog-button.default.primary.text',
                                                 timeout=10000)
                    await page.click('button.Button.confirm-dialog-button.default.primary.text')
                    print("🟢 Кнопка 'Я не бот' нажата")
                else:
                    print("⚠️ Кнопка 'Я не бот' не найдена")
            else:
                print("⚠️ Сообщение с нужным классом не найдено")
        else:
            print("⚠️ Нет групп сообщений")


        iframe_element = await page.wait_for_selector('iframe.OmY14FFl', timeout=10000)
        iframe_src = await iframe_element.get_attribute('src')

        print(iframe_src)

        await asyncio.Future()