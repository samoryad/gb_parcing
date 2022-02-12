import requests
import json
from lesson_01.common.utils import get_configs

CONFIGS = get_configs()

username = 'samoryad'
url = f'https://api.vk.com/method/groups.get?v=5.131&access_token=' \
      f'{CONFIGS.get("token")}'
response = requests.get(url)
json_data = response.json()
# print(json_data)
print(
    f'Список id групп пользователя: {json_data.get("response").get("items")}')

with open('samoryad_vk_groups.json', 'w') as f:
    json_repo = json.dump(json_data.get("response").get("items"), f)
