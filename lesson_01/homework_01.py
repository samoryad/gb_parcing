import requests
import json

username = 'samoryad'
url = f'https://api.github.com/users/{username}/repos'
response = requests.get(url)
json_data = response.json()
print(f'Ответ: {json_data}')

repo = []
for item in json_data:
    repo.append(item['name'])
print(f'Список репозиториев пользователя {username}:')
print(repo)

with open('samoryad_repos.json', 'w') as f:
    json.dump(repo, f)
