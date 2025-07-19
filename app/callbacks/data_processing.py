"""
Exports: register_callbacks(app) (no top-level code, only functions)

Purpose: Wires together all the app’s "heavy lifting" — data loading, processing, settings management, and UI updates.

Major Callbacks:

1. Settings Update:
    Inputs: Toolbar elements

    Output: app-state-store['data']

    Purpose: Sync UI state to global app state.

2. Output Update:

    Inputs: Uploads, sample data buttons, settings

    Outputs: Dataframes, plots, empty state, download options, rule boxes, toolbar

    Purpose: End-to-end update of all UI/display elements as user interacts.

Pattern: Reactive chain — changes in controls or data upload → update app state → recalculate & update outputs/UI.
"""

from dash import Output, Input, State, html, dcc, dash_table, ctx, ALL, MATCH
# Import your utility functions
from components.rule_boxes import create_rule_boxes
from utils.data_loader import parse_csv, load_predefined_dataset
from utils.data_processor import calculate_capability, calculate_control_stats, add_control_rules
from utils.slider_defaults import get_slider_defaults
from utils.chart_creator import create_control_chart, make_stats_panel
from components.settings_toolbar import create_settings_toolbar
from callbacks.rule_checkbox import get_active_rules


def register_data_processing_callbacks(app):
    # Callback to update the app state when settings change
    @app.callback(
        Output('app-state-store', 'data', allow_duplicate=True),
        [Input('sl-range-slider', 'value'),
        Input('dropdown-period-type', 'value'),
        Input('input-process-change', 'value'),
        Input('input-y-axis-label', 'value')],
        [State('app-state-store', 'data')],
        prevent_initial_call=True
    )
    def update_app_state_settings(range_slider, period_type, process_change, y_axis_label, current_data):
        """Update the app state with settings values"""
        print("Slider callback fired, value:", range_slider)
        # Initialize app state if None
        if current_data is None:
            current_data = {}
        
        # Initialize settings if not present
        if 'settings' not in current_data:
            current_data['settings'] = {}
            
        # Update only the properties that have changed
        if ctx.triggered_id == 'sl-range-slider' and range_slider is not None:
            current_data['settings']['lsl'] = range_slider[0]
            current_data['settings']['usl'] = range_slider[1]
        elif ctx.triggered_id == 'dropdown-period-type' and period_type is not None:
            current_data['settings']['period_type'] = period_type
        elif ctx.triggered_id == 'input-process-change' and process_change is not None:
            current_data['settings']['process_change'] = process_change
        elif ctx.triggered_id == 'input-y-axis-label' and y_axis_label is not None:
            current_data['settings']['y_axis_label'] = y_axis_label
        
        return current_data
    
    @app.callback(
        [Output('stats-panel-container', 'children'),
        Output('plot-container', 'children'),
        Output('output-data-upload', 'children'),
        Output('stored-data', 'data'),
        Output('empty-state', 'style'),
        Output('processed-data-store', 'data'),
        Output('download-container', 'style'),
        Output('rule-boxes-container', 'children'),
        Output('upload-card', 'className'),
        Output('btn-in-control', 'className'),
        Output('btn-out-of-control', 'className'),
        Output('settings-toolbar-container', 'children'),
        Output('settings-toolbar-container', 'style')],
        [Input('upload-data', 'contents'),
        Input('btn-in-control', 'n_clicks'),
        Input('btn-out-of-control', 'n_clicks'),
        Input('app-state-store', 'data')],
        [State('upload-data', 'filename'),
        State('stored-data', 'data')]
    )
    def update_output(contents, in_control_clicks, out_control_clicks, app_state, filename, stored_data):
        """Update the output based on user interactions"""
        print("app_state in update_output:", app_state)

        empty_state_style = {'margin': '40px auto', 'maxWidth': '800px'} # Default visible
        download_container_style = {'display': 'none'} # Default hidden
        settings_toolbar_style = {'display': 'none'} # Default hidden
        
        # Default classes for buttons
        upload_class = 'option-card upload-card'
        in_control_class = 'option-card'
        out_control_class = 'option-card'
        
        # Get active rules from the app state
        active_rules = get_active_rules(app_state)
        
        if not ctx.triggered:
            # No triggers, return empty outputs with visible empty state
            return html.Div(style={'display': 'none'}),html.Div(style={'display': 'none'}), None, None, empty_state_style, None, download_container_style, create_rule_boxes(), upload_class, in_control_class, out_control_class, None, settings_toolbar_style
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Set active class based on triggered button
        if trigger_id == 'upload-data' and contents is not None:
            upload_class += ' active'
        elif trigger_id == 'btn-in-control' and in_control_clicks > 0:
            in_control_class += ' active'
        elif trigger_id == 'btn-out-of-control' and out_control_clicks > 0:
            out_control_class += ' active'
        
        df = None
        dataset_name = None
        
        # If the app state changed, but we have stored data, reprocess it
        if trigger_id == 'app-state-store' and stored_data and 'dataset_name' in stored_data:
            dataset_name = stored_data['dataset_name']
            if dataset_name.startswith('in_control'):
                df = load_predefined_dataset('in_control.csv')
            elif dataset_name.startswith('out_of_control'):
                df = load_predefined_dataset('out_of_control.csv')
            else:
                # Need to ask the user to reload their custom data since we can't access it after upload
                return html.Div(style={'display': 'none'}), html.Div([
                    html.P("To apply rule changes to your custom data, please re-upload your file.", className="warning-text")
                ]), None, stored_data, {'display': 'none'}, None, {'display': 'none'}, create_rule_boxes(), upload_class, in_control_class, out_control_class, {'display': 'none'}
        elif trigger_id == 'upload-data' and contents is not None:
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
            return html.Div(style={'display': 'none'}), html.Div(style={'display': 'none'}), html.Div(style={'display': 'none'}), stored_data, empty_state_style, None, download_container_style, create_rule_boxes(), upload_class, in_control_class, out_control_class, settings_toolbar_style
        if df is None:
            return html.Div(style={'display': 'none'}),html.Div('Error processing the data.'), html.Div(style={'display': 'none'}), None, empty_state_style, None, download_container_style, create_rule_boxes(), upload_class, in_control_class, out_control_class, None, settings_toolbar_style
        
        # Process the data with active rules
        df = df.rename({df.columns[0]: "value"}).with_row_index()
        stats = calculate_control_stats(df)
        
        defaults = get_slider_defaults((stats['min'], stats['max']))
        settings = app_state.get('settings', {}) if app_state else {}

        lsl_value = settings.get('lsl', defaults['lsl'])
        usl_value = settings.get('usl', defaults['usl'])
        
        capability = calculate_capability(stats['mean'], stats['std_dev'], usl_value, lsl_value)
        df_with_rules = add_control_rules(df, stats, active_rules)
        
        # Create the plot with active rules
        fig = create_control_chart(df_with_rules, stats, capability or {}, active_rules, settings)
        plot_component = dcc.Graph(figure=fig)
        stats_panel = make_stats_panel(stats, capability)
        
        # Create the data table
        data_info = html.Div([
            html.Div([
                html.Img(src='/assets/csv_icon.svg', className='data-source-icon'),
                html.H5(f'Data source: {dataset_name}')
            ], className='data-source-header'),
            html.H6(f'Number of observations: {df_with_rules.shape[0]}'),
            dash_table.DataTable(
                data=df_with_rules.drop("index").to_dicts(),
                columns=[
                    {"name": i, "id": i} for i in df_with_rules.drop("index").columns
                    if not i.startswith('rule_') or active_rules.get(int(i.split('_')[1]), True)
                ],
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
                        'if': {'filter_query': ' || '.join([f'{{{c}}} = "Broken"' for c in df_with_rules.columns if c.startswith('rule_') and active_rules.get(int(c.split('_')[1]), True)])},
                        'backgroundColor': 'rgba(255, 240, 240, 0.7)'
                    },
                    {
                        'if': {'filter_query': ' || '.join([f'{{{c}}} = "Broken"' for c in df_with_rules.columns if c.startswith('rule_') and active_rules.get(int(c.split('_')[1]), True)]), 'column_id': 'value'},
                        'fontWeight': 'bold',
                        'color': '#dc3545'
                    }
                ] + [
                    {
                        'if': {'column_id': c, 'filter_query': '{' + c + '} = "Broken"'},
                        'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                        'color': '#dc3545',
                        'fontWeight': 'bold'
                    } for c in [col for col in df_with_rules.columns if col.startswith('rule_') and active_rules.get(int(col.split('_')[1]), True)]
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
        settings_toolbar = create_settings_toolbar((stats['min'], stats['max']))
        settings_toolbar_style = {
            'display': 'block'
            }
        
        return stats_panel, plot_component, data_info, stored_data, empty_state_style, processed_data, download_container_style, create_rule_boxes(), upload_class, in_control_class, out_control_class, settings_toolbar, settings_toolbar_style
