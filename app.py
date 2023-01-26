import dash
import json2dash

configuration_file = "configuration.json"

dic_app = json2dash.json2dash.read_configuration_json(configuration_file)

app = dash.Dash(
    dic_app['name'],
    meta_tags = json2dash.format_meta_tags(dic_app)
)

app.title = dic_app['name']

app.config.suppress_callback_exceptions = True
app.dic_app = dic_app