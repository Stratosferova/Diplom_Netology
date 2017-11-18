# Вывести список групп в ВК в которых состоит пользователь, но не
# состоит никто из его друзей. В качестве жертвы, на ком тестировать, можно
# использовать: https://vk.com/tim_leary

import requests
from urllib.parse import urlencode
import json
import time
import configparser

AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
config = configparser.ConfigParser()
config.read('token.ini')
CLIENT_ID = config['data']['client_id']
access_token = config['data']['token']

ERR_RATELIMIT = 6 #ошибка если обращений в секунду слишком много
ERR_FORBID = 7 #если пользователь закрыл свои группы
ERR_BAN = 18 #если удален или забанен
    
def get_friends(access_token, **kwargs):
    kwargs.update({
        'access_token': access_token,
        'v': '5.68'
    })
    friends = None
    while True:
        try:
            response_data = requests.get('https://api.vk.com/method/friends.get', kwargs).json()
            friends = response_data['response']['items']
        except requests.RequestException:
            time.sleep(1)
            continue
        except KeyError:
            if response_data['error']['error_code'] == ERR_RATELIMIT: 
                time.sleep(1)
                continue
        break
    return(friends)

def get_groups(access_token, **kwargs):
    kwargs.update({
        'access_token': access_token,
        'v': '5.68'
    })
    groups = None
    while True:
        try:
            response_data = requests.get('https://api.vk.com/method/groups.get', kwargs).json()
            groups = response_data['response']['items']
        except requests.RequestException:
            time.sleep(1)
            continue
        except KeyError:
            if response_data['error']['error_code'] == ERR_RATELIMIT: 
                time.sleep(1)
                continue
            elif response_data['error']['error_code'] == ERR_FORBID: 
                pass
            elif response_data['error']['error_code'] == ERR_BAN: 
                pass
        break
    return(groups)

def main():
    users = get_friends(access_token)
    groups = get_groups(access_token, extended=1, fields='id,name,members_count')
    groups_dict = { g['id']: g for g in groups }
    for i, user in enumerate(users):
        user_groups = get_groups(access_token, user_id=user)
        if not user_groups:
            continue
        for group_id in user_groups:
            try:
                del groups_dict[group_id] 
            except KeyError:
                pass
    groups = []
    for item in groups_dict.values():
        groups.append({'id':item['id'], 'name':item['name'],'members_count':item['members_count']})
    print(groups) 
    
    with open('groups.json', 'w', encoding='utf-8') as outfile:
        json.dump(groups, outfile, indent=2, ensure_ascii=True) 
        
if __name__ == '__main__':
    main()
