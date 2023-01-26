from dash.dependencies import Input, Output
import json2dash
from app import app

app.dics, app.layouts = json2dash.initialize(app.dic_app)

app.layout = json2dash.start_page_layout(app)

server = app.server

@app.callback(
    Output('div_main', 'children'),
    [
        Input('url', 'pathname')
    ]
)
def display_layout(pathname):
    return json2dash.route(pathname, app)

if __name__ == '__main__':
    app.run_server(debug=True)