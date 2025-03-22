import base64
import io
import polars as pl
import plotnine as p9
from plotly.tools import mpl_to_plotly
import matplotlib.pyplot as plt
from io import BytesIO
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
from flask import Flask

# Initialize Flask and Dash
server = Flask(__name__)
app = Dash(__name__, server=server)

# Define the layout
app.layout = html.Div([
    html.H1('Lean Six Sigma - Control Chart Rules Detection'),
    
    # Upload component (button to upload csv)
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Select CSV with single column of numeric data'
        ]),
        style={
            'width': '100%',
            'maxWidth': '500px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '12px',
            'borderColor': '#4a90e2',
            'background': '#f8f9fa',
            'textAlign': 'center',
            'margin': '20px auto',
            'color': '#4a90e2',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'fontWeight': '500',
            'cursor': 'pointer',
            'transition': 'all 0.2s ease',
            'position': 'relative',
            'top': '0',
            'boxShadow': '0 2px 4px rgba(74, 144, 226, 0.1)',
        }
    ),

    # Plot container (will be used later)
    html.Div(id='plot-container'),
    
    # Download button (disabled for now)
    html.Button(
        'Download Plot',
        id='btn-download',
        style={'display': 'none'}  # Hidden until we implement plotting
    ),

    # Display the uploaded data info
    html.Div(id='output-data-upload')
    
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
        return pl.read_csv(io.StringIO(decoded), columns=[0])
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return None



@callback(
    Output('plot-container', 'children'),
    Input('upload-data', 'contents')
)
def update_plot(contents):
    """Create and display a control chart plot when data is uploaded"""
    if contents is None:
        return html.Div('Upload a file to see the plot.')
    
    df = parse_csv(contents)
    if df is None:
        return html.Div('Error processing the file for plotting.')
    
    # Data manipulation
    df = df\
        .rename({df.columns[0]: "value"})\
        .with_row_index()

    # Adding mean, std dev, and control limits
    mean = df['value'].mean()
    std_dev = df['value'].std()
    upper_control_limit = mean + 3 * std_dev
    lower_control_limit = mean - 3 * std_dev
    usl = mean + 2 * std_dev  # Upper 2-sigma Limit
    lsl = mean - 2 * std_dev  # Lower 2-sigma Limit
    usl_1 = mean + 1 * std_dev  # Upper 1-sigma Limit
    lsl_1 = mean - 1 * std_dev  # Lower 1-sigma Limit    

    # Create plotnine plot
    plot = (p9.ggplot(df, p9.aes(x='index', y='value'))
            + p9.geom_line()
            + p9.theme_minimal()
            + p9.geom_hline(yintercept=mean, color='red', linetype='dashed')
            + p9.geom_hline(yintercept=usl, color='blue', linetype='dashed')
            + p9.geom_hline(yintercept=lsl, color='blue', linetype='dashed')
            + p9.geom_hline(yintercept=usl_1, color='green', linetype='dashed')
            + p9.geom_hline(yintercept=lsl_1, color='green', linetype='dashed')
            + p9.geom_hline(yintercept=upper_control_limit, color='orange', linetype='dashed')
            + p9.geom_hline(yintercept=lower_control_limit, color='orange', linetype='dashed')
            + p9.labs(title='Time Series Plot', 
                     x='Observation',
                     y='Value'))
    
    # Save plot to bytes buffer
    buffer = BytesIO()
    plot.save(buffer, format='png', dpi=300, width=10, height=6)
    buffer.seek(0)
    
    # Convert to base64 for display
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return html.Img(src=f'data:image/png;base64,{image_base64}',
                    style={'width': '100%', 'max-width': '800px'})


@callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def show_uploaded_data(contents, filename):
    """Update the output div when a file is uploaded"""
    if contents is None:
        return html.Div('No file uploaded yet.')
    
    df = parse_csv(contents)
    if df is None:
        return html.Div('Error processing the file.')
    
    return html.Div([
        html.H5(f'Uploaded file: {filename}'),
        html.H6(f'Shape: {df.shape}'),
        dash_table.DataTable(
            data=df.to_dicts(),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_table={
                'height': '300px',
                'width': '200px',
                'overflowY': 'auto',
                'overflowX': 'auto'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'minWidth': '100px'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
    ])

if __name__ == '__main__':
    app.run(debug=True) 