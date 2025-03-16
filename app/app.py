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
    html.H1('Lean Six Sigma - Control Chart Rules Detection'),
    
    # Upload component
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Select CSV with single column of numeric data'
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '2px',
            'borderStyle': 'solid',
            'borderRadius': '6px',
            'borderColor': '#9e9e9e',
            'background': 'linear-gradient(180deg, #d6d6d6 0%, #9e9e9e 100%)',
            'textAlign': 'center',
            'margin': '10px',
            'color': '#1a1a1a',
            'fontFamily': '"Arial Narrow", sans-serif',
            'fontWeight': 'bold',
            'boxShadow': 'inset 0 -2px 4px rgba(0,0,0,0.3), 0 2px 6px rgba(0,0,0,0.3)',
            'cursor': 'pointer',
            'textTransform': 'uppercase',
            'letterSpacing': '1px',
            'borderTop': '2px solid #ffffff',
            'borderLeft': '2px solid #ffffff',
            'borderRight': '2px solid #6e6e6e',
            'borderBottom': '2px solid #6e6e6e'
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
    """Parse uploaded CSV file contents from Dash Upload component"""
    if contents is None:
        return None
    
    try:
        # Remove the data URI prefix (e.g., 'data:text/csv;base64,')
        content_string = contents.split(',')[1]
        # Decode base64 and convert to DataFrame
        decoded = base64.b64decode(content_string).decode('utf-8')
        return pl.read_csv(io.StringIO(decoded))
    except Exception as e:
        print(f"Error parsing CSV: {e}")
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