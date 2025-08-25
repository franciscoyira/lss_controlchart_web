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
        Input('checklist-period-comparison', 'value'))
    def toggle_slider_enabled_state(checklist_value):
      print(checklist_value)
      if checklist_value is None:
        disabled=True
        tooltip={"placement": "top", "always_visible": False}
        value=0
      elif 'period_comparison' not in checklist_value:
        disabled=True
        tooltip={"placement": "top", "always_visible": False}
        value=0
      else:
        disabled=False
        tooltip={"placement": "top", "always_visible": True}
        value=50
      print(disabled, tooltip, value)
      return disabled, tooltip, value