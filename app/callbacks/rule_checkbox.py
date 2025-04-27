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

# Callback to update app state store when any checkbox changes
@callback(
    Output('app-state-store', 'data', allow_duplicate=True),
    [Input(f'rule-check-{i}', 'value') for i in range(1, 9)],
    [State('app-state-store', 'data')],
    prevent_initial_call=True
)
def update_rule_state(*args):
    """Update the rule state when any checkbox changes"""
    # Last element in args is the current app state
    checkbox_values = args[:-1]
    current_state = args[-1] or {}
    
    # Initialize rules dict if it doesn't exist
    if 'rules' not in current_state:
        current_state['rules'] = {}
    
    # Update rule states
    for i, value in enumerate(checkbox_values, 1):
        current_state['rules'][f'rule-{i}'] = bool(value and f'rule-{i}' in value)
    
    return current_state

# Callback to update rule box appearance when app state changes
@callback(
    [Output(f'rule-box-{i}', 'className') for i in range(1, 9)],
    [Input('app-state-store', 'data')]
)
def update_rule_boxes(app_state):
    """Update the rule box appearance based on app state"""
    if not app_state or not isinstance(app_state, dict) or 'rules' not in app_state:
        # Return default classes if no state is provided
        return ['rule-box selected' for _ in range(8)]
    
    # Get the rule states from app state
    rule_state = app_state.get('rules', {})
    
    classes = []
    for i in range(1, 9):
        rule_key = f'rule-{i}'
        is_selected = rule_state.get(rule_key, True)
        classes.append('rule-box selected' if is_selected else 'rule-box')
    return classes