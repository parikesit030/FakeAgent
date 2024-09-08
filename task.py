import requests
import urllib.parse
from fake_useragent import UserAgent
import time
import json
from colorama import Fore, init

init(autoreset=True)

def extract_username(authorization):
    try:
        parsed_data = urllib.parse.parse_qs(authorization)
        user_data_json = parsed_data.get('user', [''])[0]

        user_data = json.loads(urllib.parse.unquote(user_data_json))

        username = user_data.get('username', 'tidak dikenal')
        return username
    except (json.JSONDecodeError, KeyError):
        return 'tidak dikenal'


def load_authorizations_with_usernames(file_path):
    with open(file_path, 'r') as file:
        authorizations = file.readlines()

    auth_with_usernames = [{'authorization': auth.strip(), 'username': extract_username(auth)} for auth in
                           authorizations]
    return auth_with_usernames


def claim_tasks(authorization, username):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'authorization': authorization.strip(),
        'origin': 'https://telegram.agent301.org',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    url_get_tasks = 'https://api.agent301.org/getMe'
    response = requests.post(url_get_tasks, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        if json_response.get("ok"):
            result = json_response.get("result", {})
            balance = result.get("balance", 0)
            print(f"{Fore.LIGHTYELLOW_EX}account {Fore.LIGHTWHITE_EX}{username} {Fore.LIGHTYELLOW_EX}balance: {Fore.LIGHTWHITE_EX}{balance}AP")
            print(f"{Fore.LIGHTYELLOW_EX}sedang memulai tugas...\n")

            tasks = result.get("tasks", [])
            for task in tasks:
                task_type = task.get("type")
                title = task.get("title")
                reward = task.get("reward", 0)
                is_claimed = task.get("is_claimed")
                count = task.get("count", 0)
                max_count = task.get("max_count")

                if max_count is None and not is_claimed:
                    claim_task(headers, task_type, title)

                elif task_type == "video" and count < max_count:
                    while count < max_count:
                        print(f"{Fore.LIGHTYELLOW_EX}tugas {task_type} - {title} {Fore.LIGHTWHITE_EX}progress: {count}/{max_count}")
                        if claim_task(headers, task_type, title):
                            count += 1
                        else:
                            break

                elif not is_claimed and count >= max_count:
                    claim_task(headers, task_type, title)

        else:
            print(f"{Fore.LIGHTRED_EX}Gagal mendapatkan tugas. silakan coba lagi.")
    else:
        print(f"{Fore.LIGHTRED_EX}kesalahan: {response.status_code}")


def claim_task(headers, task_type, title):
    url_complete_task = 'https://api.agent301.org/completeTask'
    claim_data = {"type": task_type}
    response = requests.post(url_complete_task, headers=headers, json=claim_data)

    if response.status_code == 200 and response.json().get("ok"):
        result = response.json().get("result", {})
        task_reward = result.get("reward", 0)
        balance = result.get("balance", 0)
        print(
            f"{Fore.LIGHTYELLOW_EX}tugas {task_type} - {title} - reward {Fore.LIGHTWHITE_EX}{task_reward}AP - Текущий баланс: {Fore.LIGHTWHITE_EX}{balance}AP")
        return True
    else:
        print(f"{Fore.LIGHTRED_EX}tugas {task_type} - {title} - Gagal mengeksekusi!!")
        return False

def claim_tasks_whell(authorization):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'authorization': authorization.strip(),
        'origin': 'https://telegram.agent301.org',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    url_get_tasks = 'https://api.agent301.org/wheel/load'
    response = requests.post(url_get_tasks, headers=headers)


    if response.status_code == 200:
        json_response = response.json()
        if json_response.get("ok"):
            tasks = json_response.get("result", {}).get("tasks", {})

            for _ in range(5):
                payload = {'type': 'hour'}
                requests.post('https://api.agent301.org/wheel/task', headers=headers, json=payload)
                print(f'{Fore.LIGHTYELLOW_EX}Menyelesaikan tugas')

            if tasks.get('daily', 1) == 0:
                payload = {'type': 'daily'}
                requests.post('https://api.agent301.org/wheel/task', headers=headers, json=payload)
                print(f'{Fore.LIGHTYELLOW_EX}Menyelesaikan tugas harian')

            if not tasks.get('bird', True):
                payload = {'type': 'bird'}
                requests.post('https://api.agent301.org/wheel/task', headers=headers, json=payload)
                print(f'{Fore.LIGHTYELLOW_EX}Menyelesaikan tugas')

def main():
    auth_data = load_authorizations_with_usernames('query.txt')

    while True:
        for account_number, data in enumerate(auth_data, start=1):
            authorization = data['authorization']
            username = data['username']


            print(f"\n{Fore.LIGHTYELLOW_EX}------------------------------------")
            print(f"{Fore.LIGHTYELLOW_EX}akun {Fore.LIGHTWHITE_EX}№{account_number}  ")
            print(f"{Fore.LIGHTYELLOW_EX}------------------------------------")

            claim_tasks(authorization, username)
            claim_tasks_whell(authorization)
        print(f"{Fore.LIGHTWHITE_EX}Semua tugas berhasil diselesaikan!")
        
        break
        # Если нужен сон на 24 часа, то вместо break написать это: time.sleep(86400)

if __name__ == "__main__":
    main()
