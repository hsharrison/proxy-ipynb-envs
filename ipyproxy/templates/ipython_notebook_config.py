c = get_config()

c.NotebookApp.base_url = '{{ env.url }}'
c.NotebookApp.ip = '127.0.0.1'
c.NotebookApp.trust_xheaders = True
c.NotebookApp.webapp_setting = {
    'static_url_prefix': '{{ env.url }}'
}
c.NotebookApp.port = {{ env.port }}
