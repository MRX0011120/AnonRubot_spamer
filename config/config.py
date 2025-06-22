from pathlib import Path
from colorama import Fore, Style, init
init()

#для красоты
green = Fore.GREEN
red = Fore.RED
yellow = Fore.YELLOW
brigth = Style.BRIGHT
ress = Style.RESET_ALL

# путь до папки, вроде корневой
current_directory = Path(__file__).resolve().parent
template_directory = current_directory.parent / 'templates'
config_directory = current_directory.parent / 'config'

# путь к прокси
proxy_path = template_directory / 'proxy.txt'

# путь к конфигу
config_path = config_directory / 'config.txt'

with open(config_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

    spam_text_AnonRubot_1 = str(lines[0]).split('=')[1].strip()
    spam_text_AnonRubot_2 = str(lines[1]).split('=')[1].strip()
    age_AnonRubot = str(lines[2]).split('=')[1].strip()

with open(proxy_path, 'r') as file:
    proxy_data = file.readline().strip()

    proxy_parts = proxy_data.split('@')
    host_port = proxy_parts[0]
    username_password = proxy_parts[1].split(':')

    proxy = {
        'host': host_port.split(':')[0],
        'port': int(host_port.split(':')[1]),
        'username': username_password[0],
        'password': username_password[1]
    }

API_ID = 2040
API_HASH = 'b18441a1ff607e10a989891a5462e627'
TIMEZONE = 'UTC'