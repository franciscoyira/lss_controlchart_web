from dash import html, dcc, dash_table
from components.settings_toolbar import create_settings_toolbar

def create_layout():
    """Create the main app layout"""
    return html.Div([
        html.H1('Lean Six Sigma - Control Chart Rules Detection', className='app-header'),
        
        # Card-style layout for data selection options
        html.Div([
            # Upload CSV Card
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        html.Img(src='/assets/upload_icon.svg', className='card-icon'),
                        html.Div("Upload your own CSV")
                    ], className='card-content'),
                    className='upload-component'
                ),
            ], id='upload-card', className='option-card upload-card'),
            
            # In-control Data Card
            html.Div([
                html.Div([
                    html.Img(src='/assets/chart_icon.svg', className='card-icon'),
                    html.Div("Try in-control data")
                ], className='card-content')
            ], id='btn-in-control', className='option-card'),
            
            # Out-of-control Data Card
            html.Div([
                html.Div([
                    html.Img(src='/assets/warning_icon.svg', className='card-icon'),
                    html.Div("Try out-of-control data")
                ], className='card-content')
            ], id='btn-out-of-control', className='option-card'),
        ], className='data-options-container'),

        # Empty state container - shows only when no data is loaded
        html.Div([
            html.Img(src='/assets/control-chart-icon.svg', className='empty-state-icon'),
            html.H2('Welcome to the Control Chart Analyzer', className='empty-state-heading'),
            html.P('Start by uploading your data or selecting one of the example datasets above.',
                  className='empty-state-text'),
            html.P('This tool will analyze your process data against the 8 Nelson rules to identify unusual variation.',
                  className='empty-state-text')
        ], id='empty-state', className='empty-state'),
        
        # Settings toolbar - shown only when data is loaded
        html.Div(
            create_settings_toolbar(),
            id='settings-toolbar-container',
            style={'display': 'none'}  # Initially hidden
        ),
        
        # Rule boxes container - just create an empty container
        html.Div([
            html.H3("Nelson Rules for Control Charts", className="rule-section-title"),
            # rule_boxes will be added here in app.py
        ], id='rule-boxes-container', className='rule-boxes-container'),
        
        # Plot container
        html.Div(id='plot-container'),

        # Display the uploaded data info
        html.Div(id='output-data-upload'),
        
        # Download buttons
        html.Div([
            html.Button(
                'Download Plot',
                id='btn-download',
                className='hidden'
            ),
            html.Button([
                html.Img(src='/assets/download_icon.svg', className='button-icon'),
                'Download Data with Rules'
            ],
                id='btn-download-data',
                className='action-button'
            ),
            dcc.Download(id='download-dataframe-csv'),
        ], id='download-container', className='download-container'),
        
        # Store for the current data
        dcc.Store(id='stored-data'),
        dcc.Store(id='processed-data-store'),
        
        # Note: rule-state-store will be added in app.py
        
        # Footer with references
        create_footer()
    ])

def create_footer():
    """Create the footer component with references"""
    return html.Div([
        html.Hr(className='footer-hr'),
        html.Div([
            # References section with updated heading style
            html.H6("References", className='references-heading'),
            html.P([
                "Nelson, L.S. (1984). The Shewhart Control Chart—Tests for Special Causes. ",
                html.I("Journal of Quality Technology"), 
                " 16(4), 238-239. ", 
                html.A("https://doi.org/10.1080/00224065.1984.11978921", 
                       href="https://doi.org/10.1080/00224065.1984.11978921", 
                       target="_blank"),
                html.Br(),
                "Office of the Secretary of Defense, Quality Management Office (1989). Small Business Guidebook to Quality Management, pp. 45-46, 63-64. ",
                html.A("https://apps.dtic.mil/sti/pdfs/ADA310869.pdf", 
                       href="https://apps.dtic.mil/sti/pdfs/ADA310869.pdf", 
                       target="_blank")
            ], className='references-text'),
            
            # Creator attribution with link to portfolio
            html.Div([
                html.Span("Made by ", className='creator-text'),
                html.A("Francisco Yirá", 
                       href="https://cv.franciscoyira.com/", 
                       target="_blank",
                       className='creator-link'),
                html.Span(" in Toronto, Canada ", className='creator-text'),
                html.Span("🍁", className='emoji')
            ], className='creator-attribution')
        ], className='footer-content')
    ], className='app-footer')
