# coding: utf-8

# Вывести список групп в ВК в которых состоит пользователь, но не
# состоит никто из его друзей. В качестве жертвы, на ком тестировать, можно
# использовать: https://vk.com/tim_leary

import requests
import json
import time
import configparser

config = configparser.ConfigParser()
config.read('token.ini')
USER_ID = config['data']['user_id']
access_token = config['data']['token']

ERR_RATELIMIT = 6 
    
def vk_method(method, access_token, **kwargs):
    kwargs.update({
        'access_token': access_token,
        'v': '5.68',
    })
    result = None
    while True:
        try:
            print('{} -'.format(time.ctime()))
            response_data = requests.get('https://api.vk.com/method/' + method, kwargs).json()
            result = response_data['response']['items']
        except requests.RequestException:
            time.sleep(1)
            continue
        except KeyError:
            if response_data['error']['error_code'] == ERR_RATELIMIT: 
                time.sleep(1)
                continue
        break
    return result

def main():
    users = vk_method('friends.get', access_token, user_id=USER_ID)
    groups = vk_method('groups.get', access_token, user_id=USER_ID, extended=1, fields='id,name,members_count')
    groups_dict = { g['id']: g for g in groups }
    for user in users: 
        user_groups = vk_method('groups.get', access_token, user_id=user)
        if not user_groups:
            continue
        for group_id in user_groups:
            if group_id in groups_dict:
                del groups_dict[group_id]
            else:
                pass
    groups = []
    for item in groups_dict.values(): 
        groups.append({'id': item['id'], 'name': item['name'],'members_count': item['members_count']})
    print(groups) 
    
    with open('groups.json', 'w', encoding='utf-8') as outfile:
        json.dump(groups, outfile, indent=2, ensure_ascii=True) 
        
if __name__ == '__main__':
    main()
