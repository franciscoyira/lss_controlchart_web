from dash import callback, Output, Input, State, html, dcc, dash_table, ctx
import plotly.graph_objects as go
from plotly.graph_objects import Figure
# Import your utility functions
from components.rule_boxes import create_rule_boxes
from utils.data_loader import parse_csv, load_predefined_dataset
from utils.data_processor import process_data, add_control_rules, calculate_control_limits
from utils.chart_creator import create_control_chart


def register_callbacks(app):
    @app.callback(
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
