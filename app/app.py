import base64
import io
import polars as pl
import plotly.express as px
from plotly.graph_objects import Figure
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table, ctx
from flask import Flask
import os
import plotly.graph_objects as go

from components.layout import create_layout
from components.rule_boxes import create_rule_boxes
from callbacks.data_processing import register_callbacks
from callbacks.download import register_download_callback

# Initialize Flask and Dash
server = Flask(__name__)
app = Dash(__name__, server=server)
app.layout = create_layout()

register_callbacks(app)
register_download_callback(app)


if __name__ == '__main__':
    app.run(debug=True) 