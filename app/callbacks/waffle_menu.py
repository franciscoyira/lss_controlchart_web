from dash import Input, Output, State, ALL, ctx

def register_waffle_menu_callbacks(app):
    @app.callback(
        Output('waffle-menu', 'className'),
        [
            Input('waffle-menu-button', 'n_clicks'),
            Input('upload-data-menu', 'contents'),
            Input({'type': 'sample-data-menu-btn', 'index': ALL}, 'n_clicks')
        ],
        [State('waffle-menu', 'className')],
        prevent_initial_call=True
    )
    def toggle_waffle_menu(menu_clicks, upload_contents, sample_clicks, current_class):
        """
        Toggles the visibility of the waffle menu.
        It opens on button click and closes if an item is selected.
        """
        triggered_id = ctx.triggered_id
        
        # If a menu item was clicked, always close the menu
        if triggered_id != 'waffle-menu-button':
            return 'waffle-menu hidden'
        
        # If the button was clicked, toggle the current state
        if 'hidden' in current_class:
            return 'waffle-menu'
        else:
            return 'waffle-menu hidden'
