from dash import Dash, html
from flask import Flask

from components.layout import create_layout
from components.rule_boxes import create_rule_boxes
from callbacks.data_processing import register_callbacks
from callbacks.download import register_download_callback

# Initialize Flask and Dash
server = Flask(__name__)
app = Dash(__name__, server=server)

layout = create_layout()

# Add rule boxes to the layout after it's created
rule_boxes_container = next(div for div in layout.children if getattr(div, 'id', None) == 'rule-boxes-container')
if rule_boxes_container:
    rule_boxes_grid = create_rule_boxes()
    rule_boxes_container.children.append(rule_boxes_grid)

# Add the rule-state-store div
layout.children.append(html.Div(id='rule-state-store', style={'display': 'none'}))

# Set the app layout
app.layout = layout

register_callbacks(app)
register_download_callback(app)

if __name__ == '__main__':
    app.run(debug=True) 