
# coding: utf-8

# Вывести список групп в ВК в которых состоит пользователь, но не
# состоит никто из его друзей. В качестве жертвы, на ком тестировать, можно
# использовать: https://vk.com/tim_leary

# In[1]:

import requests
from urllib.parse import urlencode
import json
import time


# In[2]:

AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
CLIENT_ID = 5030613
REDIRECT_URI = ''


# In[10]:

auth_data = {
    'client_id': CLIENT_ID,
    'display': 'popup',
    'response_type': 'token',
    'scope': 'friends, status',
    'v': '5.68'
}

token_url = '?'.join((AUTHORIZE_URL, urlencode(auth_data)))

access_token = '5dfd6b0dee902310df772082421968f4c06443abecbc082a8440cb18910a56daca73ac8d04b25154a1128'
params = {
    'access_token': access_token,
    'v': '5.68',
    #'fields': 'id, name, members_count'
}


# In[17]:

response = requests.get('https://api.vk.com/method/friends.get', params) #список друзей пользователя
users = (response.json()['response']['items'])
print(users)


# In[5]:

response_groups = requests.get('https://api.vk.com/method/groups.get', {
    'access_token': access_token,
    'v': '5.68',
    'extended': 1,
    'fields': 'id,name,members_count',
})
groups = (response_groups.json()['response'])
print(groups) #выводим группы пользователя 


# In[12]:

groups['items'] #cмотрим на них еще раз, но в более читаемом варианте


# In[7]:

groups_dict = { g['id']: g for g in groups['items'] }
print(groups_dict.keys()) #выводим все id, чтобы помотреть потом пересечение с группами других пользователей


# In[19]:

for i, user in enumerate(users):
    while True:
        response_groups_friends = requests.get('https://api.vk.com/method/groups.get',{
            'access_token': access_token,
            'v': '5.68',
            'user_id': user,
        })
        response_data = response_groups_friends.json()
        try:
            #print(user, response_data['response']) #позволяет распечатать список групп, но для задачи это не нужно
            for group_id in response_data['response']['items']:
                try:
                    del groups_dict[group_id] #удаляем из списка исходного пользоватял те группы, что есть у друзей
                except KeyError:
                    pass
        except KeyError:
            #print('ERROR', response_data['error']) #выводит все ошибки - для нашей задачи это не нужно
            if response_data['error']['error_code'] == 6: #ошибка если обращений в секунду слишком много
                time.sleep(1)
                continue
            elif response_data['error']['error_code'] == 7: #если пользователь закрыл свои группы
                pass
            elif response_data['error']['error_code'] == 18: #если удален или забанен
                pass
        break
        


# In[20]:

print(groups_dict) #смотрим что осталось после удаления


# In[21]:

print([g['name'] for g in groups_dict.values()]) #просто смотрим названия групп


# In[22]:

groups = []
for item in groups_dict.values():
    groups.append({'id':item['id'], 'name':item['name'],'members_count':item['members_count']})
    print(groups) #приводим данные в порядок для json


# In[23]:

with open('groups.json', 'w', encoding='utf-8') as outfile:
    json.dump(groups, outfile, indent=2, ensure_ascii=True) #сохраняем ответ в json


# In[ ]:



