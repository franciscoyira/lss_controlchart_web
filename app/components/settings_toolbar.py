from dash import html, dcc

def create_settings_toolbar(range_data = None):
    """Create a horizontal toolbar for settings with labels to the left of their controls"""
    
    min_data, max_data, step = 1, 10, 1
    if range_data and len(range_data) == 2:
        min_data = range_data[0]
        max_data = range_data[1]
        step = (max_data - min_data)/5
        
    return html.Div([
        # USL (Upper Specification Limit)
        html.Div([
            html.Label(
                "Upper and Lower Specification Limits:", className="toolbar-label"),
            # TODO: make the slider values come from the data
            dcc.RangeSlider(
                min=min_data,
                max=max_data,
                step=step,
                className='toolbar-rangeslider',
                value=[5, 10],
                id='sl-range-slider',
                persistence=True,
                persistence_type='memory')
        ], className="toolbar-item"),
        
        # Periods naming dropdown
        html.Div([
            html.Label("Period Type:", className="toolbar-label"),
            dcc.Dropdown(
                id="dropdown-period-type",
                options=[
                    {"label": "Days", "value": "days"},
                    {"label": "Weeks", "value": "weeks"},
                    {"label": "Months", "value": "months"}
                ],
                value="days",
                clearable=False,
                className="toolbar-dropdown",
                searchable=False,
                persistence=True,
                persistence_type='memory'
            )
        ], className="toolbar-item"),
        
        # Process change point
        html.Div([
            html.Label("Process Change at:", className="toolbar-label"),
            dcc.Input(
                id="input-process-change",
                type="number",
                placeholder="Enter value",
                min=0,
                step=1,
                className="toolbar-textbox-input",
                style={"width": "85px"},
                persistence=True,
                persistence_type='memory'
            )
        ], className="toolbar-item"),
        
        # Y-axis label
        html.Div([
            html.Label("Y-axis Label:", className="toolbar-label"),
            dcc.Input(
                id="input-y-axis-label",
                type="text",
                value="Value",
                className="toolbar-textbox-input",
                style={"width": "100px"},
                persistence=True,
                persistence_type='memory'
            )
        ], className="toolbar-item"),
        
    ], id="settings-toolbar", className="settings-toolbar")