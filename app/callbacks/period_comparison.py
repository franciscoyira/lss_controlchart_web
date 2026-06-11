""" 
**`callbacks/period_comparison.py`**

**Purpose:** This callback module is responsible for managing the state of the process change slider 
and its corresponding input field.

**Functionality:**
- It enables or disables the process change slider and input based on whether the "Period Comparison" checkbox is checked.
- It synchronizes the values between the slider and the numeric input.
- It updates the slider's range and marks based on the length of the uploaded data.

**Callback Signatures:**
1. **Input:** `checklist-period-comparison.value`, `data-store.data`
   **Output:** `input-process-change.disabled`, `input-process-change-input.disabled`, `input-process-change.max`, `input-process-change-input.max`, `input-process-change.marks`
2. **Input:** `input-process-change.value`
   **Output:** `input-process-change-input.value`
3. **Input:** `input-process-change-input.value`
   **Output:** `input-process-change.value`
"""

from dash import Input, Output, State

def register_period_comparison_callbacks(app):
    @app.callback(
        Output('input-process-change', 'disabled'),
        Output('input-process-change', 'tooltip'),
        Output('input-process-change', 'value'),
        Output('input-process-change', 'min'),
        Output('input-process-change', 'max'),
        Input('checklist-period-comparison', 'value'),
        State('processed-data-store', 'data'),
        State('app-state-store', 'data')
        )
    def toggle_slider_enabled_state(checklist_value, data):
      slider_min = 0
      enabled = bool(checklist_value) and 'period_comparison' in checklist_value
      if not enabled or not data:
        disabled = True
        tooltip = {"placement": "top", "always_visible": False}
        value = 0
        slider_max = 100
      else:
        disabled = False
        tooltip = {"placement": "top", "always_visible": True}
        slider_max = len(data)
        # Default to the midpoint, clamped to the dataset size
        value = min(50, slider_max // 2)
      return disabled, tooltip, value, slider_min, slider_max