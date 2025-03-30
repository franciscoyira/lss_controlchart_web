from dash import Input, Output, callback, ALL, MATCH
import json

def get_active_rules(rule_state_json):
    """
    Parse the rule state JSON and return a dictionary of active rules
    
    Args:
        rule_state_json (str): JSON string from rule-state-store
        
    Returns:
        dict: Dictionary with rule numbers as keys and boolean values
    """
    if not rule_state_json:
        # If no state provided, all rules are active by default
        return {i: True for i in range(1, 9)}
        
    try:
        rule_state = json.loads(rule_state_json)
        active_rules = {}
        for i in range(1, 9):
            rule_key = f'rule-{i}'
            active_rules[i] = rule_state.get(rule_key, True)
        return active_rules
    except:
        # Return all active if there's an error
        return {i: True for i in range(1, 9)}

# Callback to update rule state store when any checkbox changes
@callback(
    Output('rule-state-store', 'children'),
    [Input(f'rule-check-{i}', 'value') for i in range(1, 9)]
)
def update_rule_state(*checkbox_values):
    """Update the rule state when any checkbox changes"""
    rule_state = {}
    for i, value in enumerate(checkbox_values, 1):
        rule_state[f'rule-{i}'] = bool(value and f'rule-{i}' in value)
    return json.dumps(rule_state)

# Callback to update rule box appearance when checkbox state changes
@callback(
    [Output(f'rule-box-{i}', 'className') for i in range(1, 9)],
    [Input('rule-state-store', 'children')]
)
def update_rule_boxes(rule_state_json):
    """Update the rule box appearance based on checkbox state"""
    if not rule_state_json:
        # Return default classes if no state is provided
        return ['rule-box selected' for _ in range(8)]
        
    try:
        rule_state = json.loads(rule_state_json)
        classes = []
        for i in range(1, 9):
            rule_key = f'rule-{i}'
            is_selected = rule_state.get(rule_key, True)
            classes.append('rule-box selected' if is_selected else 'rule-box')
        return classes
    except:
        # Return default in case of error
        return ['rule-box selected' for _ in range(8)]