import os
import re
import json
import time
import requests
import pyfiglet
import asyncio
import aiohttp
import threading
import random
import logging
from bs4 import BeautifulSoup
from termcolor import colored

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    ascii_banner = pyfiglet.figlet_format("   NATRA", font="slant")
    print(colored(ascii_banner, 'cyan', attrs=['bold']))
    print("=" * 60)
    print(colored("       Tool Treo Mess & Dis By Natra Socola", 'white', attrs=['bold']))
    print("=" * 60)

def get_uid(cookie):
    try:
        return re.search(r'c_user=(\d+)', cookie).group(1)
    except:
        return '0'

def get_fb_dtsg_jazoest(cookie, target_id):
    try:
        response = requests.get(
            f'https://mbasic.facebook.com/privacy/touch/block/confirm/?bid={target_id}',
            headers={ 'cookie': cookie, 'user-agent': 'Mozilla/5.0' }
        ).text
        fb_dtsg = re.search('name="fb_dtsg" value="([^"]+)"', response).group(1)
        jazoest = re.search('name="jazoest" value="([^"]+)"', response).group(1)
        return fb_dtsg, jazoest
    except:
        return None, None

def get_eaag_token(cookie):
    try:
        res = requests.get(
            'https://business.facebook.com/business_locations',
            headers={ 'cookie': cookie, 'user-agent': 'Mozilla/5.0' }
        )
        return re.search(r'EAAG\w+', res.text).group()
    except:
        return None

def send_message(idbox, fb_dtsg, jazoest, cookie, message_body):
    try:
        uid = get_uid(cookie)
        timestamp = int(time.time() * 1000)
        data = {
            'thread_fbid': idbox,
            'action_type': 'ma-type:user-generated-message',
            'body': message_body,
            'client': 'mercury',
            'author': f'fbid:{uid}',
            'timestamp': timestamp,
            'offline_threading_id': str(timestamp),
            'message_id': str(timestamp),
            'source': 'source:chat:web',
            '__user': uid,
            '__a': '1',
            '__req': '1b',
            '__rev': '1015919737',
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest
        }
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post('https://www.facebook.com/messaging/send/', data=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f'Lỗi gửi tới ID {idbox}: {e}')
        return False

def worker(cookie_data, id_list, message_list, base_delay):
    name = cookie_data['name']
    cookie = cookie_data['cookie']

    while True:
        try:
            fb_dtsg, jazoest = get_fb_dtsg_jazoest(cookie, id_list[0])
            if not fb_dtsg or not jazoest:
                print(f"Không lấy được fb_dtsg/jazoest")
                time.sleep(60)
                continue

            for idbox in id_list:
                for message_body in message_list:
                    success = send_message(idbox, fb_dtsg, jazoest, cookie, message_body)
                    if success:
                        print(f"Gửi tin nhắn thành công tới: {idbox}")
                    else:
                        print(f"Gửi tin nhắn thất bại tới: {idbox}")
                    
                    delay = base_delay + random.uniform(-0.5, 0.5)
                    if delay < 0:
                        delay = 0
                    time.sleep(delay)
        except Exception as err:
            print(f"Lỗi không xác định: {err}")
            time.sleep(60)

def treo_mess():
    id_list = []
    while True:
        idbox = input(colored("Nhập ID Box (Nhập 'done' để dừng): ", 'yellow', attrs=['bold'])).strip()
        if idbox.lower() in ['done']:
            break
        if idbox.isdigit():
            id_list.append(idbox)

    cookie_list = []
    while True:
        ck = input(colored("Nhập cookie (Nhập 'done' để dừng): ", 'yellow', attrs=['bold'])).strip()
        if ck.lower() in ['done']:
            break
        if 'c_user=' in ck and 'xs=' in ck:
            cookie_list.append(ck)

    file_list = []
    while True:
        name_file = input(colored("Nhập file.txt (Nhập 'done' để dừng): ", 'yellow', attrs=['bold'])).strip()
        if name_file.lower() in ['done']:
            break
        if name_file.endswith('.txt'):
            file_list.append(name_file)

    base_delay = int(input(colored('Nhập delay: ', 'yellow', attrs=['bold'])))

    user_data_list = []
    for index, ck in enumerate(cookie_list, 1):
        try:
            uid = get_uid(ck)
            token = get_eaag_token(ck)

            if token:
                res = requests.get(
                    f'https://graph.facebook.com/{uid}?fields=name&access_token={token}',
                    headers={'cookie': ck, 'user-agent': 'Mozilla/5.0'}
                ).json()
                name = res.get('name', f'User_{index}')
            else:
                name = f'User_{index}'

            user_data_list.append({'name': name, 'id': uid, 'cookie': ck})
        except Exception as e:
            print(f"[{index}] Lỗi lấy thông tin user: {e}")

    message_list = []
    for f in file_list:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if content:
                    message_list.append(content)
        except Exception as e:
            print(f'Lỗi đọc file {f}: {e}')

    if not user_data_list:
        print("Không có cookie hợp lệ để chạy.")
        return
    if not id_list:
        print("Không có ID Box nào được nhập.")
        return
    if not message_list:
        print("Không có nội dung tin nhắn để gửi.")
        return

    for data in user_data_list:
        thread = threading.Thread(target=worker, args=(data, id_list, message_list, base_delay), daemon=True)
        thread.start()

    print("Đã bắt đầu gửi tin nhắn")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Đã dừng chương trình")

def spam_discord():
    async def validate_token(session, token):
        headers = {"Authorization": token}
        try:
            async with session.get("https://discord.com/api/v9/users/@me", headers=headers) as r:
                return token if r.status == 200 else None
        except:
            return None

    async def process_tokens(token_file):
        with open(token_file, "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
        async with aiohttp.ClientSession() as session:
            tasks = [validate_token(session, token) for token in tokens]
            results = await asyncio.gather(*tasks)
        valid_tokens = [token for token in results if token]
        return valid_tokens

    async def send_once(session, token, channel_id, message):
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        json_data = {"content": message}
        try:
            async with session.post(
                f"https://discord.com/api/v9/channels/{channel_id}/messages",
                headers=headers, json=json_data
            ) as response:
                await handle_response(response, token, channel_id)
        except Exception as e:
            print(f"Token ({token[:30]}...) gửi lỗi: {e}")

    async def handle_response(response, token, channel_id):
        if response.status == 200:
            print(f"Gửi tin nhắn thành công tới: {channel_id}")
        elif response.status == 429:
            try:
                data = await response.json()
                retry_after = data.get("retry_after", 5)
                print(f"Token bị giới hạn, đợi {retry_after} giây")
                await asyncio.sleep(retry_after)
            except:
                await asyncio.sleep(5)
        else:
            print(f"Gửi tin nhắn thất bại tới: {channel_id}")

    async def start_spam(tokens, channel_ids, message, delay):
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = []
                for token in tokens:
                    for channel_id in channel_ids:
                        tasks.append(send_once(session, token, channel_id, message))
                await asyncio.gather(*tasks)
                await asyncio.sleep(delay)

    token_file = input(colored("Nhập file token: ", 'magenta', attrs=['bold']))
    tokens = asyncio.run(process_tokens(token_file))
    if not tokens:
        print(colored("Không có token hợp lệ.", 'red', attrs=['bold']))
        return

    channel_input = input(colored("Nhập ID kênh (phân tách bằng dấu phẩy): ", 'magenta', attrs=['bold']))
    channel_ids = [cid.strip() for cid in channel_input.split(",") if cid.strip()]

    message_file = input(colored("Nhập file.txt: ", 'magenta', attrs=['bold']))
    try:
        with open(message_file, "r", encoding="utf-8") as f:
            message = f.read().strip()
    except FileNotFoundError:
        print(colored(f"Không tìm thấy file: {message_file}", 'red', attrs=['bold']))
        return

    if not message:
        print(colored("File không chứa nội dung nào.", 'red'))
        return

    try:
        delay = float(input(colored("Nhập delay: ", 'magenta', attrs=['bold'])))
    except:
        print(colored("Delay không hợp lệ.", 'red'))
        return

    print(f"Đã bắt đầu gửi tin nhắn")
    asyncio.run(start_spam(tokens, channel_ids, message, delay))

def main():
    clear()
    banner()
    print(colored("1. Thoát", 'red', attrs=['bold']))
    print(colored("2. Treo Spam Messenger", 'yellow', attrs=['bold']))
    print(colored("3. Treo Spam Discord", 'magenta', attrs=['bold']))
    
    choice = input(colored("Chọn chức năng: ", 'green', attrs=['bold'])).strip()
    if choice == '2':
        treo_mess()
    elif choice == '3':
        spam_discord()
    else:
        print("Thoát chương trình.")

if __name__ == '__main__':
    main()
