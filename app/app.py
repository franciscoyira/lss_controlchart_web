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

# Initialize Flask and Dash
server = Flask(__name__)
app = Dash(__name__, server=server)

# Define the layout using the imported function
app.layout = create_layout()

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
    fig.add_hline(y=limits['mean'], line_dash="dash", line_color="grey", annotation_text="Mean", annotation=dict(font_color="grey"))
    fig.add_hline(y=limits['usl'], line_dash="dash", line_color="orange", annotation_text="2σ", annotation=dict(font_color="orange"))
    fig.add_hline(y=limits['lsl'], line_dash="dash", line_color="orange")
    fig.add_hline(y=limits['usl_1'], line_dash="dash", line_color="green", annotation_text="1σ", annotation=dict(font_color="green"))
    fig.add_hline(y=limits['lsl_1'], line_dash="dash", line_color="green")
    fig.add_hline(y=limits['ucl'], line_dash="dash", line_color="red", annotation_text="3σ", annotation=dict(font_color="red"))
    fig.add_hline(y=limits['lcl'], line_dash="dash", line_color="red")
    
    # Add zone annotations to the left side for top areas
    fig.add_annotation(
        x=df['index'].min() - 2,
        y=(limits['mean'] + limits['usl_1'])/2,
        text="Zone C",
        showarrow=False,
        xref="x",
        yref="y",
        font=dict(size=12, color="green"),  # Match 1σ line color
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="green",
        borderwidth=1,
        borderpad=2
    )
    
    fig.add_annotation(
        x=df['index'].min() - 2,
        y=(limits['usl'] + limits['usl_1'])/2,
        text="Zone B",
        showarrow=False,
        xref="x",
        yref="y",
        font=dict(size=12, color="orange"),  # Match 2σ line color
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="orange",
        borderwidth=1,
        borderpad=2
    )
    
    fig.add_annotation(
        x=df['index'].min() - 2,
        y=(limits['ucl'] + limits['usl'])/2,
        text="Zone A",
        showarrow=False,
        xref="x",
        yref="y",
        font=dict(size=12, color="red"),  # Match 3σ line color
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="red",
        borderwidth=1,
        borderpad=2
    )
    
    # Define rule descriptions for tooltips
    rule_descriptions = {
        'rule_1': "Rule 1: Point beyond 3 sigma",
        'rule_2': "Rule 2: 9 points on same side of centerline",
        'rule_3': "Rule 3: 6 points steadily increasing/decreasing",
        'rule_4': "Rule 4: 14 points alternating up and down", 
        'rule_5': "Rule 5: 2 of 3 points in Zone A or beyond",
        'rule_6': "Rule 6: 4 of 5 points in Zone B or beyond",
        'rule_7': "Rule 7: 15 points in Zone C",
        'rule_8': "Rule 8: 8 points with none in Zone C"
    }
    
    # Create arrays for scatter plot with highlighted points
    indices = []
    values = []
    hover_texts = []
    colors = []
    
    # Identify broken rules for each point
    rule_columns = [col for col in df.columns if col.startswith('rule_')]
    
    for row in df.iter_rows(named=True):
        broken_rules = []
        
        for rule in rule_columns:
            if row[rule] == "Broken":
                rule_num = rule.split('_')[1]
                broken_rules.append(f"{rule_descriptions[rule]}")
        
        if broken_rules:
            indices.append(row['index'])
            values.append(row['value'])
            # Add value to hover text with the value formatted to 2 decimal places
            value_text = f"<b>Value: {row['value']:.2f}</b>"
            hover_texts.append(value_text + "<br>" + "<br>".join(broken_rules))
            colors.append("red")  # All points with violations are red
    
    # Add highlighted points for rule violations
    if indices:
        fig.add_trace(
            go.Scatter(
                x=indices,
                y=values,
                mode='markers',
                marker=dict(
                    color=colors,
                    size=10,
                    line=dict(
                        color='black',
                        width=1
                    )
                ),
                text=hover_texts,
                hoverinfo='text',
                name='Rule Violations'
            )
        )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Observation",
        yaxis_title="Value",
        showlegend=False,
        hovermode='closest'
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
     Output('empty-state', 'style'),
     Output('processed-data-store', 'data'),
     Output('download-container', 'style'),
     Output('rule-boxes-container', 'children')],
    [Input('upload-data', 'contents'),
     Input('btn-in-control', 'n_clicks'),
     Input('btn-out-of-control', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('stored-data', 'data')]
)
def update_output(contents, in_control_clicks, out_control_clicks, filename, stored_data):
    """Update the output based on user interactions"""
    empty_state_style = {'margin': '40px auto', 'maxWidth': '800px'} # Default visible
    download_container_style = {'display': 'none'} # Default hidden
    
    if not ctx.triggered:
        # No triggers, return empty outputs with visible empty state
        return html.Div(), None, None, empty_state_style, None, download_container_style, create_rule_boxes()
    
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
        return html.Div('Upload a file or select a predefined dataset.'), html.Div(), stored_data, empty_state_style, None, download_container_style, create_rule_boxes()
    
    if df is None:
        return html.Div('Error processing the data.'), html.Div(), None, empty_state_style, None, download_container_style, create_rule_boxes()
    
    # Process the data
    df_with_rules, limits = process_data(df)
    
    # Create the plot
    fig = create_control_chart(df_with_rules, limits)
    plot_component = dcc.Graph(figure=fig)
    
    # Create the data table
    data_info = html.Div([
        html.Div([
            html.Img(src='/assets/csv_icon.svg', className='data-source-icon'),
            html.H5(f'Data source: {dataset_name}')
        ], className='data-source-header'),
        html.H6(f'Number of observations: {df_with_rules.shape[0]}'),
        dash_table.DataTable(
            data=df_with_rules.drop("index").to_dicts(),
            columns=[{"name": i, "id": i} for i in df_with_rules.drop("index").columns],
            style_table={
                'height': '300px',
                'maxWidth': '100%',
                'overflowY': 'auto',
                'overflowX': 'auto',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'border': '1px solid #e9ecef'
            },
            cell_selectable=False,
            style_cell_conditional=[
                {'if': {'column_id': 'value'}, 'textAlign': 'right'}
            ] + [
                {'if': {'column_id': c}, 'textAlign': 'center'} for c in [col for col in df_with_rules.columns if col.startswith('rule_')]
            ],
            style_cell={
                'padding': '10px 15px',
                'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif',
                'fontSize': '14px',
                'color': '#495057'
            },
            style_data={'border': '1px solid #e9ecef'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{rule_1} = "Broken" || {rule_2} = "Broken" || {rule_3} = "Broken" || {rule_4} = "Broken" || {rule_5} = "Broken" || {rule_6} = "Broken" || {rule_7} = "Broken" || {rule_8} = "Broken"'},
                    'backgroundColor': 'rgba(255, 240, 240, 0.7)'
                },
                {
                    'if': {'filter_query': '{rule_1} = "Broken" || {rule_2} = "Broken" || {rule_3} = "Broken" || {rule_4} = "Broken" || {rule_5} = "Broken" || {rule_6} = "Broken" || {rule_7} = "Broken" || {rule_8} = "Broken"', 'column_id': 'value'},
                    'fontWeight': 'bold',
                    'color': '#dc3545'
                }
            ] + [
                {
                    'if': {'column_id': c, 'filter_query': '{' + c + '} = "Broken"'},
                    'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                    'color': '#dc3545',
                    'fontWeight': 'bold'
                } for c in [col for col in df_with_rules.columns if col.startswith('rule_')]
            ],
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'border': '1px solid #e9ecef',
                'borderBottom': '2px solid #dee2e6',
                'color': '#0062cc',
                'textAlign': 'left',
                'padding': '12px 15px',
                'fontFamily': '"Inter", "Segoe UI", system-ui, sans-serif'
            }
        )
    ], className='data-info-container')
    
    # Store current data
    stored_data = {'dataset_name': dataset_name}
    
    # Store processed data for download
    processed_data = df_with_rules.to_dicts()
    
    # Hide empty state and show download button when data is loaded
    empty_state_style = {'display': 'none'}
    download_container_style = {'display': 'block', 'marginBottom': '10px'}
    
    return plot_component, data_info, stored_data, empty_state_style, processed_data, download_container_style, create_rule_boxes()

@callback(
    Output('download-dataframe-csv', 'data'),
    Input('btn-download-data', 'n_clicks'),
    State('processed-data-store', 'data'),
    State('stored-data', 'data'),
    prevent_initial_call=True,
)
def download_csv(n_clicks, processed_data, stored_data):
    """Download the dataset with rules as a CSV file"""
    if n_clicks is None or processed_data is None:
        return None
    
    # Convert the stored data back to a polars DataFrame
    df = pl.DataFrame(processed_data)
    
    # Generate filename based on the original dataset name
    filename = "rules_" + (stored_data.get('dataset_name', 'dataset') if stored_data else 'dataset')
    
    # Use StringIO to capture the CSV output
    csv_buffer = io.StringIO()
    df.write_csv(csv_buffer)
    csv_string = csv_buffer.getvalue()
    
    # Return CSV data directly
    return dict(
        content=csv_string,
        filename=filename,
        type='text/csv'
    )

if __name__ == '__main__':
    app.run(debug=True) 