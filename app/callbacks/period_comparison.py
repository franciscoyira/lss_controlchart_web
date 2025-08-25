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
    def toggle_slider_enabled_state(checklist_value, processed_data, app_state):
      min_val=0
      max_val = len(processed_data['data']) if processed_data and 'data' in processed_data else 100
      
      settings = app_state.get('settings', {}) if app_state else {}
      # Get the persisted value, default to the midpoint if not available
      process_change_value = settings.get('process_change', max_val // 2)

      if checklist_value and 'period_comparison' in checklist_value:
        disabled=False
        tooltip={"placement": "top", "always_visible": True}
        # Use the persisted value, ensuring it's within the current data's bounds
        if process_change_value is not None and min_val <= process_change_value <= max_val:
            value = process_change_value
        else:
            value = max_val // 2
      else:
        disabled=True
        tooltip={"placement": "top", "always_visible": False}
        # When disabled, the value doesn't matter as much, but we can reset to 0
        # The important part is that the persisted value in app-state-store is not cleared.
        value=0

      return disabled, tooltip, value, min_val, max_val