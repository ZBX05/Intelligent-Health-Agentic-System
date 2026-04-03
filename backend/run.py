from web import web_config,app
from gevent import pywsgi

if __name__ == '__main__':
    app.run(web_config.app_host,web_config.app_port)
    # # app.run(web_config.app_host,web_config.app_port,ssl_context=(web_config.app_cert_dir,web_config.app_key_dir))
    # server=pywsgi.WSGIServer((web_config.app_host,web_config.app_port),app,certfile=r'F:\project\health_agentic_system\backend\ssl\server.crt'
    #                          ,keyfile=r'F:\project\health_agentic_system\backend\ssl\server.key')
    # server.serve_forever()