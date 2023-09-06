import os

from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig

os.system('kill -9 $(pgrep ngrok)')
webhook_url = ngrok.connect(addr='127.0.0.1:8080', pyngrok_config=PyngrokConfig(start_new_session=True))
print (webhook_url)