import requests

token_id = "7afed9ab-d4f2-4688-bd53-131d56ab0206"

r = requests.get('https://webhook.site/token/'+ token_id +'/requests?sorting=newest')

for request in r.json()['data']:
    print(request)