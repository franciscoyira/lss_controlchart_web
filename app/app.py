import base64
import io
import polars as pl
from dash import Dash, html, dcc, callback, Output, Input, State
from flask import Flask

# Initialize Flask
server = Flask(__name__)

# Initialize Dash
app = Dash(__name__, server=server)

# Define the layout
app.layout = html.Div([
    html.H1('Data Visualization Dashboard'),
    
    # Upload component
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select CSV File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    
    # Display the uploaded data info
    html.Div(id='output-data-upload'),
    
    # Plot container (will be used later)
    html.Div(id='plot-container'),
    
    # Download button (disabled for now)
    html.Button(
        'Download Plot',
        id='btn-download',
        style={'display': 'none'}  # Hidden until we implement plotting
    ),
])

def parse_csv(contents):
    """Parse uploaded CSV file contents"""
    if contents is None:
        return None
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        # Read CSV using Polars
        df = pl.read_csv(io.StringIO(decoded.decode('utf-8')))
        return df
    except Exception as e:
        print(e)
        return None

@callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    """Update the output div when a file is uploaded"""
    if contents is None:
        return html.Div('No file uploaded yet.')
    
    df = parse_csv(contents)
    if df is None:
        return html.Div('Error processing the file.')
    
    return html.Div([
        html.H5(f'Uploaded file: {filename}'),
        html.H6('Data Preview:'),
        html.Pre(str(df.head())),
        html.H6(f'Shape: {df.shape}')
    ])

if __name__ == '__main__':
    app.run(debug=True) 