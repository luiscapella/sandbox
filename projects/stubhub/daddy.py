import json
from pprint import pprint
import urllib3

url = 'https://www.stubhub.com/daddy-yankee-orlando-tickets-8-26-2022/event/105240006/'

http = urllib3.PoolManager()


data = http.request('GET', url)

print(data.data)

print("hello world")