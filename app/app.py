import polars as pl
import plotly.express as px
from plotly.graph_objects import Figure
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table, ctx
from flask import Flask
import plotly.graph_objects as go
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

try:
    # Import components separately to avoid circular imports
    from app.components.layout import create_layout
    from app.components.rule_boxes import create_rule_boxes
    import app.callbacks.rule_checkbox
    from app.callbacks.data_processing import register_callbacks
    from app.callbacks.download import register_download_callback

    # Initialize Flask and Dash
    server = Flask(__name__)
    app = Dash(__name__, server=server)

    logger.info("Creating application layout")
    layout = create_layout()

    # Add rule boxes to the layout after it's created
    rule_boxes_container = next((div for div in layout.children if getattr(div, 'id', None) == 'rule-boxes-container'), None)
    if rule_boxes_container:
        rule_boxes_grid = create_rule_boxes()
        rule_boxes_container.children.append(rule_boxes_grid)
    else:
        logger.warning("Could not find rule-boxes-container in layout")

    # Add the rule-state-store div
    layout.children.append(html.Div(id='rule-state-store', style={'display': 'none'}))

    # Set the app layout
    app.layout = layout

    logger.info("Registering callbacks")
    register_callbacks(app)
    register_download_callback(app)

    logger.info("Application setup complete")
except Exception as e:
    logger.error(f"Error during application initialization: {e}", exc_info=True)
    raise

if __name__ == '__main__':
    logger.info("Starting development server")
    app.run(debug=True)
else:
    # In production
    logger.info(f"Application initialized in production mode. Working directory: {os.getcwd()}")
    # Log available files in the data directory for debugging
    try:
        data_dir = os.path.join('data', 'test')
        if os.path.exists(data_dir):
            logger.info(f"Files in {data_dir}: {os.listdir(data_dir)}")
        else:
            logger.warning(f"Data directory {data_dir} not found")
    except Exception as e:
        logger.warning(f"Could not check data directory: {e}") 