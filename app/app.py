from dash import Dash, html, dcc
from flask import Flask

from components.layout import create_layout
from callbacks.data_processing import register_data_processing_callbacks
from callbacks.download import register_download_callback
from callbacks.waffle_menu import register_waffle_menu_callbacks

# Initialize Flask and Dash
server = Flask(__name__)
app = Dash(__name__, server=server, suppress_callback_exceptions=True)

layout = create_layout()

# Set the app layout
app.layout = layout

register_data_processing_callbacks(app)
register_download_callback(app)
register_waffle_menu_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True) 