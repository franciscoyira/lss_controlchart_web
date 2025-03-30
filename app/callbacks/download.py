import io
import polars as pl
from dash import callback, Output, Input, State

def register_download_callback(app):
    @app.callback(
        Output('download-dataframe-csv', 'data'),
        Input('btn-download-data', 'n_clicks'),
        State('processed-data-store', 'data'),
        State('stored-data', 'data'),
        prevent_initial_call=True,
    )
    def download_csv(n_clicks, processed_data, stored_data):
        """Download the dataset with rules as a CSV file"""
        if n_clicks is None or processed_data is None:
            return None
        
        # Convert the stored data back to a polars DataFrame
        df = pl.DataFrame(processed_data)
        
        # Generate filename based on the original dataset name
        filename = "rules_" + (stored_data.get('dataset_name', 'dataset') if stored_data else 'dataset')
        
        # Use StringIO to capture the CSV output
        csv_buffer = io.StringIO()
        df.write_csv(csv_buffer)
        csv_string = csv_buffer.getvalue()
        
        # Return CSV data directly
        return dict(
            content=csv_string,
            filename=filename,
            type='text/csv'
        )
