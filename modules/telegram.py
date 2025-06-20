import asyncio.constants

import socks
print("socks module path:", socks.__file__)


from playwright.async_api import async_playwright
from telethon.sync import TelegramClient
from config.config import proxy, API_ID, API_HASH

async def connect_to_telegram(session_path, api_id = API_ID, api_hash = API_HASH):
    client = TelegramClient(session_path, api_id, api_hash, proxy=(socks.SOCKS5, proxy['host'], proxy['port'], proxy['username'], proxy['password']))
    await client.connect()
    if not await client.is_user_authorized():
        print(f"{session_path} - НЕВАЛИД")
        return None
    else:
        print(f"{session_path} - ВЗЯЛ СЕССИЮ В РАБОТУ")
        return client

async def connect_to_web_telegram(numbers_from_session, code_tg=None, code_queue=None):
    async with async_playwright() as p:
        proxy_socks = {
            "server": f"http://{proxy['host']}:{proxy['port']}",
            "username" : f"{proxy['username']}",
            "password": f"{proxy['password']}"
        }
        browser = await p.firefox.launch(
            headless=True,
            proxy=proxy_socks
        )
        print(proxy_socks)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://web.telegram.org/a/", wait_until="domcontentloaded", timeout=120_000)

        login = await page.wait_for_selector("text=LOG IN BY PHONE NUMBER", timeout=120_000)
        await login.click()

        # await page.wait_for_selector("div.input-field-input[contenteditable='true'][inputmode='decimal']",
        #                              timeout=60000,
        #                              state='attached')
        number_input = await page.wait_for_selector("input#sign-in-phone-number", timeout=30000)
        # number_input = page.locator("input#sign-in-phone-number")
        # await number_input.wait_for(timeout=60000)
        await number_input.click()
        print('TG - НАЖАЛ НА ПОЛЕ С НОМЕРОМ')



        await page.keyboard.press('Control+A')
        # print('выделил весь текст')
        await page.keyboard.press('Backspace')
        # print('удалил весь текст')

        await number_input.fill(f"+{numbers_from_session}")
        # print("✅ Поле с номером телефона заполнено")

        await page.keyboard.press('Enter')

        await page.wait_for_selector("input#sign-in-code", timeout=30000)
        code_input = page.locator("input#sign-in-code")
        await code_input.wait_for(timeout=30000)
        await code_input.click()

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

        # ya_ne_bot = await last_message.query_selector('button.Button.tiny.primary.has-ripple')
        # await ya_ne_bot.click()



        await asyncio.Future()