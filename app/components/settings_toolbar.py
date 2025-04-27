from dash import html, dcc

def create_settings_toolbar():
    """Create a horizontal toolbar for settings with labels to the left of their controls"""
    return html.Div([
        # USL (Upper Specification Limit)
        html.Div([
            html.Label("USL:", className="toolbar-label"),
            dcc.Input(
                id="input-usl",
                type="number",
                placeholder="Enter value",
                className="toolbar-input",
                step=0.01,
                persistence=True,
                persistence_type='memory'
            )
        ], className="toolbar-item"),
        
        # LSL (Lower Specification Limit)
        html.Div([
            html.Label("LSL:", className="toolbar-label"),
            dcc.Input(
                id="input-lsl",
                type="number",
                placeholder="Enter value",
                className="toolbar-input",
                step=0.01,
                persistence=True,
                persistence_type='memory'
            )
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
                className="toolbar-input",
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
                className="toolbar-input",
                style={"width": "100px"},
                persistence=True,
                persistence_type='memory'
            )
        ], className="toolbar-item"),
        
    ], id="settings-toolbar", className="settings-toolbar") 