from dash import Input, Output
from app.components.rule_boxes import create_rule_boxes

def register_rule_boxes_callbacks(app):
    """Register callbacks related to the rule boxes positioning"""
    
    @app.callback(
        [Output('rule-boxes', 'children'),
         Output('rule-boxes-container', 'style'),
         Output('empty-state', 'style'),
         Output('plot-container', 'style')],
        [Input('stored-data', 'data')]
    )
    def update_rule_boxes_position(data):
        """Position rule boxes based on whether data is loaded or not"""
        # Create the rule boxes content
        rule_boxes_content = create_rule_boxes()
        
        if data is None or not data:
            # No data - show empty state, position rule boxes below it
            return (
                rule_boxes_content,
                {'margin-top': '20px'},
                {'display': 'block'},  # Show empty state
                {'display': 'none'}    # Hide plot container
            )
        else:
            # Data loaded - hide empty state, show rule boxes above plot
            return (
                rule_boxes_content,
                {'margin-bottom': '30px'},
                {'display': 'none'},    # Hide empty state
                {'display': 'block'}    # Show plot container
            )