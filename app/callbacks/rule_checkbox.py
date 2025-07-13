from dash import Input, Output, callback, ALL, MATCH, State
import json

def get_active_rules(app_state):
    """
    Parse the app state and return a dictionary of active rules
    
    Args:
        app_state (dict): App state from app-state-store
        
    Returns:
        dict: Dictionary with rule numbers as keys and boolean values
    """
    if not app_state or not isinstance(app_state, dict):
        # If no state provided, all rules are active by default
        return {i: True for i in range(1, 9)}
    
    # Get the rules section from the app state
    rules = app_state.get('rules', {})
    
    if not rules:
        # If no rules in state, all rules are active by default
        return {i: True for i in range(1, 9)}
        
    # Create dictionary of active rules
    active_rules = {}
    for i in range(1, 9):
        rule_key = f'rule-{i}'
        active_rules[i] = rules.get(rule_key, True)
    
    return active_rules

@callback(
    Output('app-state-store', 'data', allow_duplicate=True),
    [Input(f'rule-check-{i}', 'value') for i in range(1, 9)],
    [State('app-state-store', 'data')],
    prevent_initial_call=True
)
def update_rule_state(*args):
    """Update the rule state when any checkbox changes"""
    checkbox_values = args[:-1] # [Input(f'rule-check-{i}'... list of 8 lists (each from a checkbox)
    current_state = args[-1] or {} # [State('app-state-store'... the current state dict from the store
    
    # Writing the checkboxes values to the current state
    current_state['rules'] = {
        f'rule-{i}': bool(val) 
        for i, val in enumerate(checkbox_values, 1)
    }
    
    return current_state

@callback(
    [Output(f'rule-box-{i}', 'className') for i in range(1, 9)],
    [Input('app-state-store', 'data')]
)
def update_rule_boxes(app_state):
    """Update the rule box appearance based on app state"""
    rule_state = (app_state or {}).get('rules', {})
    
    return [
        'rule-box selected' if rule_state.get(f'rule-{i}', True) else 'rule-box'
        for i in range(1, 9)
    ]