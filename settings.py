wsgi_app = "main:app"
bind = "127.0.0.1:19071"
workers = 4
timeout = 300

accesslog = '-'
errorlog = '-'