""" 
**`components/settings_toolbar.py`**

**Exports:** `create_settings_toolbar(range_data=None)`
**Purpose:** Returns a Div containing the *settings toolbar* UI (controls for upper/lower limits, period type, process change, y-label).

**Major Elements:**

  * `dcc.RangeSlider` (id: `sl-range-slider`): sets USL/LSL, min/max optionally set via `range_data`
  * `dcc.Dropdown` (id: `dropdown-period-type`)
  * `dcc.Input` (id: `input-process-change`)
  * `dcc.Input` (id: `input-y-axis-label`)
* **Pattern:** UI factory; most are hardcoded, but `range_data` is dynamic.

"""

from dash import html, dcc
from utils.slider_defaults import get_slider_defaults, make_marks


def create_settings_toolbar(range_data = None):
    """Create a horizontal toolbar for settings with labels to the left of their controls"""
    
    # Assume you always have range_data = (min, max)
    defaults = get_slider_defaults(range_data)

    return html.Div([
        # USL (Upper Specification Limit)
        html.Div([
            html.Label(
                "Upper and Lower Specification Limits:", className="toolbar-label"),
            dcc.RangeSlider(
                min= defaults['slider_min'],
                max= defaults['slider_max'],
                dots=False,
                marks=make_marks(defaults['lsl'], defaults['usl']),
                className='toolbar-rangeslider',
                value=[defaults['lsl'], defaults['usl']],
                id='sl-range-slider',
                #pushable=step/10,
                tooltip={"placement": "top", "always_visible": True},
                persistence=True,
                persistence_type='memory')
        ], className="toolbar-item"),
        
        # Checkbox - enable Period Comparison
        html.Div([
            dcc.Checklist(
                options=[
                    {'label': 'Period Comparison',
                     'value': 'period_comparison'}
                ],
                id='checklist-period-comparison',
                className='toolbar-item',
                persistence=True,
                persistence_type='memory'
            )
        ], className="toolbar-item"),
        
        
        # Process change point
        html.Div([
            html.Label("Process Change at:", className="toolbar-label"),
            dcc.Slider(
                min=0,
                max=100,
                dots=False,
                id="input-process-change",
                className='toolbar-rangeslider',
                included=False,
                persistence=True,
                persistence_type='memory'
            )
        ], className="toolbar-item"),
        
        # Periods naming dropdown
        html.Div([
            html.Label("Period Units:", className="toolbar-label"),
            dcc.Dropdown(
            id="dropdown-period-type",
            options=[
                {"label": "Hours", "value": "Hours"},
                {"label": "Days", "value": "Days"},
                {"label": "Weeks", "value": "Weeks"},
                {"label": "Months", "value": "Months"},
                {"label": "Observations", "value": "Observations"}
            ],
            value="Days",
            clearable=False,
            className="toolbar-dropdown",
            searchable=True,
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
        ], className="toolbar-item", style={'display': 'none'}),
        
    ], id="settings-toolbar", className="settings-toolbar")