import requests
from fake_useragent import UserAgent

ua = UserAgent()
user_agent = ua.random

url = 'https://www.caranddriver.com/chevrolet/equinox/specs/'
headers={'User-Agent': user_agent}

response= requests.get(url.strip(), headers=headers, timeout=10)

