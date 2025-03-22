import base64
import io
import polars as pl
import plotly.express as px
from plotly.graph_objects import Figure
from dash import Dash, html, dcc, callback, Output, Input, State, dash_table, ctx
from flask import Flask
import os

# Initialize Flask and Dash
server = Flask(__name__)
app = Dash(__name__, server=server)

# Define the layout
app.layout = html.Div([
    html.H1('Lean Six Sigma - Control Chart Rules Detection', 
            style={
                'textAlign': 'center',
                'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif',
                'fontSize': '2.5rem',
                'fontWeight': '600',
                'color': '#fff',
                'background': 'linear-gradient(120deg, #0062cc, #0097e6, #00b894)',
                'backgroundSize': '200% 200%',
                'animation': 'gradient 15s ease infinite',
                'padding': '24px 30px',
                'marginTop': '20px',
                'marginBottom': '30px',
                'borderRadius': '8px',
                'boxShadow': '0 8px 16px rgba(0, 0, 0, 0.15)',
                'letterSpacing': '0.5px',
                'border': 'none',
            }),
    
    # Card-style layout for data selection options
    html.Div([
        # Upload CSV Card
        html.Div([
            html.Div([
                html.Img(src='/assets/upload_icon.svg', style={'height': '30px', 'margin': '10px'}),
                html.Div("Upload your own CSV", style={'textAlign': 'center'})
            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),
            dcc.Upload(
                id='upload-data',
                children=html.Div([]),
                style={
                    'position': 'absolute',
                    'top': 0,
                    'left': 0,
                    'width': '100%',
                    'height': '100%',
                    'opacity': 0,
                    'cursor': 'pointer',
                }
            ),
        ], style={
            'backgroundColor': '#f8f9fa',
            'borderRadius': '8px',
            'padding': '10px',
            'textAlign': 'center',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'flex': '1',
            'height': '100px',
            'position': 'relative',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'margin': '0 10px',
            'transition': 'transform 0.2s, box-shadow 0.2s',
            ':hover': {
                'transform': 'translateY(-5px)',
                'boxShadow': '0 5px 15px rgba(0,0,0,0.1)',
            }
        }),
        
        # In-control Data Card
        html.Div([
            html.Div([
                html.Img(src='/assets/chart_icon.svg', style={'height': '30px', 'margin': '10px'}),
                html.Div("Try in-control data", style={'textAlign': 'center'})
            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})
        ], id='btn-in-control', style={
            'backgroundColor': '#f8f9fa',
            'borderRadius': '8px',
            'padding': '10px',
            'textAlign': 'center',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'flex': '1',
            'height': '100px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'margin': '0 10px',
            'cursor': 'pointer',
            'transition': 'transform 0.2s, box-shadow 0.2s',
            ':hover': {
                'transform': 'translateY(-5px)',
                'boxShadow': '0 5px 15px rgba(0,0,0,0.1)',
            }
        }),
        
        # Out-of-control Data Card
        html.Div([
            html.Div([
                html.Img(src='/assets/warning_icon.svg', style={'height': '30px', 'margin': '10px'}),
                html.Div("Try out-of-control data", style={'textAlign': 'center'})
            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})
        ], id='btn-out-of-control', style={
            'backgroundColor': '#f8f9fa',
            'borderRadius': '8px',
            'padding': '10px',
            'textAlign': 'center',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'flex': '1',
            'height': '100px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'margin': '0 10px',
            'cursor': 'pointer',
            'transition': 'transform 0.2s, box-shadow 0.2s',
            ':hover': {
                'transform': 'translateY(-5px)',
                'boxShadow': '0 5px 15px rgba(0,0,0,0.1)',
            }
        }),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '20px auto', 'maxWidth': '800px'}),

    # Plot container (will be used later)
    html.Div(id='plot-container'),
    
    # Download button (disabled for now)
    html.Button(
        'Download Plot',
        id='btn-download',
        style={'display': 'none'}  # Hidden until we implement plotting
    ),

    # Display the uploaded data info
    html.Div(id='output-data-upload'),
    
    # Empty state container - shows only when no data is loaded
    html.Div([
        html.Img(src='/assets/control-chart-icon.svg', style={
            'height': '100px', 
            'margin': '40px auto 20px auto',
            'display': 'block'
        }),
        html.H2('Welcome to the Control Chart Analyzer', 
                style={
                    'textAlign': 'center',
                    'color': '#334155',
                    'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif',
                    'fontSize': '1.8rem',
                    'fontWeight': '600',
                    'margin': '10px 0 30px 0'
                }),
        html.P('Start by uploading your data or selecting one of the example datasets above.', 
               style={
                   'textAlign': 'center',
                   'color': '#64748b',
                   'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif',
                   'fontSize': '1.1rem',
                   'maxWidth': '600px',
                   'margin': '0 auto 15px auto',
                   'lineHeight': '1.6'
               }),
        html.P('This tool will analyze your process data against the 8 Nelson rules to identify unusual variation.',
               style={
                   'textAlign': 'center',
                   'color': '#64748b',
                   'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif',
                   'fontSize': '1.1rem',
                   'maxWidth': '600px',
                   'margin': '0 auto 50px auto',
                   'lineHeight': '1.6'
               })
    ], id='empty-state', style={'margin': '40px auto', 'maxWidth': '800px'}),
    
    # Store for the current data
    dcc.Store(id='stored-data'),
    
    #  sources footnote
    html.Div([
        html.Hr(style={'marginTop': '40px', 'marginBottom': '15px', 'opacity': '0.2'}),
        html.Div([
            # References section with updated heading style
            html.H6("References", style={
                'fontSize': '0.95rem',
                'color': '#495057',
                'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif',
                'fontWeight': '500',
                'marginBottom': '10px',
                'letterSpacing': '0.4px'
            }),
            html.P([
                "Nelson, L.S. (1984). The Shewhart Control Chart—Tests for Special Causes. ",
                html.I("Journal of Quality Technology"), 
                " 16(4), 238-239. ", 
                html.A("https://doi.org/10.1080/00224065.1984.11978921", 
                       href="https://doi.org/10.1080/00224065.1984.11978921", 
                       target="_blank"),
                html.Br(),
                "Office of the Secretary of Defense, Quality Management Office (1989). Small Business Guidebook to Quality Management, pp. 45-46, 63-64. ",
                html.A("https://apps.dtic.mil/sti/pdfs/ADA310869.pdf", 
                       href="https://apps.dtic.mil/sti/pdfs/ADA310869.pdf", 
                       target="_blank")
            ], style={
                'fontSize': '0.85rem',
                'color': '#6c757d',
                'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif',
                'lineHeight': '1.5',
                'textAlign': 'left',
                'marginBottom': '20px',
                'fontWeight': '400'
            }),
            
            # Creator attribution with link to portfolio
            html.Div([
                html.Span("Made by ", style={'color': '#6c757d'}),
                html.A("Francisco Yirá", 
                       href="https://cv.franciscoyira.com/", 
                       target="_blank",
                       style={
                           'color': '#0062cc',
                           'textDecoration': 'none',
                           'borderBottom': '1px dotted #0062cc',
                           'transition': 'color 0.2s, borderBottom 0.2s'
                       }),
                html.Span(" in Toronto, Canada ", style={'color': '#6c757d'}),
                html.Span("🍁", style={'fontSize': '0.9rem'})
            ], style={
                'fontSize': '0.85rem',
                'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif',
                'textAlign': 'center',
                'marginTop': '30px',
                'paddingTop': '15px',
                'borderTop': '1px solid rgba(0,0,0,0.05)'
            })
        ], style={
            'padding': '0 20px',
            'maxWidth': '1200px',
            'margin': '0 auto'
        })
    ], style={
        'backgroundColor': '#f8f9fa',
        'borderTop': '1px solid #e9ecef',
        'marginTop': '30px',
        'paddingBottom': '20px',
        'width': '100%',
        'position': 'relative',
        'bottom': '0'
    })
])

# Function to read predefined datasets
def load_predefined_dataset(filename):
    """Load a predefined dataset from the data/test directory"""
    file_path = os.path.join('data', 'test', filename)
    try:
        df = pl.read_csv(file_path, columns=[0])
        return df
    except Exception as e:
        print(f"Error loading predefined dataset: {e}")
        return None

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

def calculate_control_limits(df: pl.DataFrame) -> dict:
    """Calculate all control limits from the data"""
    mean = df['value'].mean()
    std_dev = df['value'].std()
    
    return {
        'mean': mean,
        'std_dev': std_dev,
        'ucl': mean + 3 * std_dev,  # Upper Control Limit
        'lcl': mean - 3 * std_dev,  # Lower Control Limit
        'usl': mean + 2 * std_dev,  # Upper 2-sigma Limit
        'lsl': mean - 2 * std_dev,  # Lower 2-sigma Limit
        'usl_1': mean + std_dev,    # Upper 1-sigma Limit
        'lsl_1': mean - std_dev,    # Lower 1-sigma Limit
    }

def add_control_rules(df: pl.DataFrame, limits: dict) -> pl.DataFrame:
    """Add control chart rules to the dataframe"""
    val_diff = pl.col('value').diff()
    in_zone_c = pl.col('value').is_between(limits['lsl_1'], limits['usl_1'])


    rule_1_counter = pl.when(pl.col("value").is_between(limits['lcl'], limits['ucl'])).then(0).otherwise(1)

    # Rule 2: 9 consecutive points on the same 
    mean_diff = (pl.col("value") - limits['mean'])
    mean_diff_sign = mean_diff.sign()
    rule_2_counter = mean_diff_sign.rolling_sum(window_size=9)

    # Rule 3: six points in a row steadily increasing or decreasing
    rule_3_counter = val_diff.sign().rolling_sum(window_size=6).abs()

    # Rule 4 - alternating pattern - 14 points in a row alternating up and down
    rule_4_counter = pl.col('value') \
        .diff() \
        .sign() \
        .diff() \
        .abs() \
        .rolling_sum(window_size=14) \
        .truediv(2)
    
    # Rule 5: Two out of three points in a row in Zone A (2 sigma) or beyond 
    # They have to be on the same side of the centerline!!
    flag_zone_a_upper = pl.when(pl.col("value") > limits['usl']).then(1).otherwise(0)
    flag_zone_a_lower = pl.when(pl.col("value") < limits['lcl']).then(1).otherwise(0)
    rule_5_counter_upper = flag_zone_a_upper.rolling_sum(window_size=3)
    rule_5_counter_lower = flag_zone_a_lower.rolling_sum(window_size=3)

    # Rule 6: Four out of five points in a row in Zone B or beyond
    rule_6_flag = pl.when(pl.col("value").is_between(limits['lsl_1'], limits['usl_1'])).then(0).otherwise(1)
    rule_6_counter = rule_6_flag.rolling_sum(window_size=5)

    # Rule 7: Fifteen points in a row within Zone C (the one closest to the centreline) 
    rule_7_flag = pl.when(pl.col("value").is_between(limits['lsl_1'], limits['usl_1'])).then(1).otherwise(0)
    rule_7_counter = rule_7_flag.rolling_sum(window_size=15)

    # Rule 8: Eight points in a row with none in Zone C (that is, 8 points beyond 1 sigma)
    # either side of the centerline (unlike rule 5)
    rule_8_flag = pl.when(~in_zone_c).then(1).otherwise(0)
    rule_8_counter = rule_8_flag.rolling_sum(window_size=8)

    return df.with_columns(
        rule_1 = pl.when(rule_1_counter > 0)
            .then(pl.lit("Broken"))
            .otherwise(pl.lit("OK")),
        rule_2 = pl.when((rule_2_counter.abs() == 9))
            .then(pl.lit("Broken"))
            .otherwise(pl.lit("OK")),
        rule_3 = pl.when(rule_3_counter == 6)
            .then(pl.lit("Broken"))
            .otherwise(pl.lit("OK")),
        rule_4 = pl.when(rule_4_counter == 14)
            .then(pl.lit("Broken"))
            .otherwise(pl.lit("OK")),
        rule_5 = pl.when((rule_5_counter_upper >= 2) | (rule_5_counter_lower >= 2))
            .then(pl.lit("Broken"))
            .otherwise(pl.lit("OK")),
        rule_6 = pl.when(rule_6_counter == 4)
            .then(pl.lit("Broken"))
            .otherwise(pl.lit("OK")),
        rule_7 = pl.when(rule_7_counter == 15)
            .then(pl.lit("Broken"))
            .otherwise(pl.lit("OK")),
        rule_8 = pl.when(rule_8_counter == 8)
            .then(pl.lit("Broken"))
            .otherwise(pl.lit("OK"))
    )

def create_control_chart(df: pl.DataFrame, limits: dict) -> Figure:
    """Create a control chart plot with all control limits"""
    # Create base plot
    fig = px.line(df, x='index', y='value', title='Control Chart Plot')
    
    # Add control limit lines
    fig.add_hline(y=limits['mean'], line_dash="dash", line_color="red", annotation_text="Mean")
    fig.add_hline(y=limits['usl'], line_dash="dash", line_color="blue", annotation_text="2σ")
    fig.add_hline(y=limits['lsl'], line_dash="dash", line_color="blue")
    fig.add_hline(y=limits['usl_1'], line_dash="dash", line_color="green", annotation_text="1σ")
    fig.add_hline(y=limits['lsl_1'], line_dash="dash", line_color="green")
    fig.add_hline(y=limits['ucl'], line_dash="dash", line_color="orange", annotation_text="3σ")
    fig.add_hline(y=limits['lcl'], line_dash="dash", line_color="orange")
    
    # Update layout
    fig.update_layout(
        xaxis_title="Observation",
        yaxis_title="Value",
        showlegend=False
    )
    
    return fig

def process_data(df):
    """Process the dataframe for display and plotting"""
    if df is None:
        return None, None
        
    # Prepare dataframe
    df = df\
        .rename({df.columns[0]: "value"})\
        .with_row_index()
    
    # Calculate limits once
    limits = calculate_control_limits(df)
    
    # Add control rules
    df_with_rules = add_control_rules(df, limits)
    
    return df_with_rules, limits

@callback(
    [Output('plot-container', 'children'),
     Output('output-data-upload', 'children'),
     Output('stored-data', 'data'),
     Output('empty-state', 'style')],
    [Input('upload-data', 'contents'),
     Input('btn-in-control', 'n_clicks'),
     Input('btn-out-of-control', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('stored-data', 'data')]
)
def update_output(contents, in_control_clicks, out_control_clicks, filename, stored_data):
    """Update the output based on user interactions"""
    empty_state_style = {'margin': '40px auto', 'maxWidth': '800px'} # Default visible
    
    if not ctx.triggered:
        # No triggers, return empty outputs with visible empty state
        return html.Div(), None, None, empty_state_style
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    df = None
    dataset_name = None
    
    if trigger_id == 'upload-data' and contents is not None:
        df = parse_csv(contents)
        dataset_name = filename
    elif trigger_id == 'btn-in-control' and in_control_clicks > 0:
        df = load_predefined_dataset('in_control.csv')
        dataset_name = 'in_control.csv'
    elif trigger_id == 'btn-out-of-control' and out_control_clicks > 0:
        df = load_predefined_dataset('out_of_control.csv')
        dataset_name = 'out_of_control.csv'
    else:
        # No valid triggers, return current state with visible empty state
        return html.Div('Upload a file or select a predefined dataset.'), html.Div(), stored_data, empty_state_style
    
    if df is None:
        return html.Div('Error processing the data.'), html.Div(), None, empty_state_style
    
    # Process the data
    df_with_rules, limits = process_data(df)
    
    # Create the plot
    fig = create_control_chart(df_with_rules, limits)
    plot_component = dcc.Graph(figure=fig)
    
    # Create the data table
    data_info = html.Div([
        html.H5(f'Data source: {dataset_name}'),
        html.H6(f'Number of observations: {df_with_rules.shape[0]}'),
        dash_table.DataTable(
            data=df_with_rules.drop("index").to_dicts(),
            columns=[{"name": i, "id": i} for i in df_with_rules.drop("index").columns],
            style_table={
                'height': '300px',
                'width': f'{100 * len(df_with_rules.columns) + 30}px',
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
    
    # Store current data
    stored_data = {'dataset_name': dataset_name}
    
    # Hide empty state when data is loaded
    empty_state_style = {'display': 'none'}
    
    return plot_component, data_info, stored_data, empty_state_style

if __name__ == '__main__':
    app.run(debug=True) 