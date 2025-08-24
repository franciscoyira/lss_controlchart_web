from dash import html, dcc
from components.rule_boxes import create_rule_boxes

# Define sample datasets in a data structure for easy extension
SAMPLE_DATASETS = [
    {
        'id': 'in-control',
        'title': 'Try in-control data',
        'description': 'Use a sample dataset representing a stable, predictable process.',
        'icon': '/assets/chart_icon.svg',
        'filename': 'in_control.csv'
    },
    {
        'id': 'out-of-control',
        'title': 'Try out-of-control data',
        'description': 'Use a sample dataset with special cause variations already present.',
        'icon': '/assets/warning_icon.svg',
        'filename': 'out_of_control.csv'
    }
]

def create_layout():
    """Create the main app layout"""
    
    # Generate sample dataset cards for the main page
    sample_dataset_cards = [
        html.Div([
            html.Div([
                html.Img(src=dataset['icon'], className='card-icon'),
                html.Div(dataset['title'])
            ], className='card-content'),
            html.P(dataset['description'], className='option-card-description')
        ], id={'type': 'sample-data-btn', 'index': dataset['id']}, className='option-card')
        for dataset in SAMPLE_DATASETS
    ]

    # Generate sample dataset items for the waffle menu
    sample_dataset_menu_items = [
        html.Div([
            html.Img(src=dataset['icon'], className='waffle-menu-item-icon'),
            html.Span(dataset['title'], className='waffle-menu-item-text')
        ], id={'type': 'sample-data-menu-btn', 'index': dataset['id']}, className='waffle-menu-item')
        for dataset in SAMPLE_DATASETS
    ]
    
    return html.Div([
        html.Div([
            # This button will toggle the menu
            html.Button(
                html.Img(
                    src="/assets/home_icon.svg",
                    alt="Menu",
                    title="Menu",
                    style={"height": "44px", "verticalAlign": "middle"}
                ),
                id="waffle-menu-button",
                className="waffle-menu-button"
            ),
            html.H1(
                'HuronSPC — Statistical Process Control Tool',
                className='app-header-title'
            ),
        ], className="app-header"),
        
        # The menu itself, hidden by default
        html.Div(id='waffle-menu', className='waffle-menu hidden', children=[
            html.A([
                html.Img(src="/assets/home_icon.svg", className='waffle-menu-item-icon'),
                html.Span("Home", className='waffle-menu-item-text')
            ], href="/", className='waffle-menu-item'),
            
            html.Hr(className='waffle-menu-divider'),
            
            # Upload Option as a menu item
            dcc.Upload(
                id='upload-data-menu',
                children=html.Div([
                    html.Img(src='/assets/upload_icon.svg', className='waffle-menu-item-icon'),
                    html.Span("Upload your own CSV", className='waffle-menu-item-text')
                ], className='waffle-menu-item'),
                style={'display': 'block'} # Make the upload component a block element
            ),
            
            # Dynamically generated sample data items
            *sample_dataset_menu_items
        ]),
        
        # Card-style layout for data selection options
        html.Div([
            # Upload CSV Card (remains a special case)
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        html.Img(src='/assets/upload_icon.svg', className='card-icon'),
                        html.Div("Upload your own CSV")
                    ], className='card-content'),
                    className='upload-component'
                ),
                html.P("Upload a .csv file with a single column of numerical data.", className='option-card-description')
            ], id='upload-card', className='option-card upload-card'),
            
            # Dynamically generated sample data cards
            *sample_dataset_cards
            
        ], id='dataset-selector', className='dataset-selector-container'),

        # Empty state container - shows only when no data is loaded
        html.Div(
            [
            html.Img(src="/assets/control-chart-icon.svg", className="empty-state-icon"),
            html.H2(
            "Welcome to HuronSPC, a Statistical Process Control Tool",
            className="empty-state-heading",
            ),
            html.P(
            [
            "HuronSPC will help you distinguish the ",
            html.Strong("signal from the noise"),
            " in your data.",
            html.Br(), html.Br(),
            "It will analyze your process data with Lean Six Sigma analysis methods (like the ",
            html.Strong("8 Nelson rules"),
            " below) to identify instances with unusual process behaviour.",
            html.Br(),
            html.P(
            "Start by uploading your data or selecting one of the example datasets above.",
            className="empty-state-text",
            ),
            ],
            className="empty-state-text",
            ),
            ],
            id="empty-state",
            className="empty-state",
        ),
        
        # Settings toolbar - shown only when data is loaded
        html.Div(
            id='settings-toolbar-container',
            style={'display': 'none'}  # Initially hidden
        ),
        
        # Rule boxes container - just create an empty container
        html.Div([
            html.H3("Nelson Rules for Control Charts", className="rule-section-title"),
            create_rule_boxes()
        ], id='rule-boxes-container', className='rule-boxes-container'),
        
        # Plot container
        html.Div(id="stats-panel-container"),
        
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
        
        # Store for UI state and settings
        dcc.Store(
            id='app-state-store',
            storage_type='memory',
            data={}),
        
        # Footer with references
        html.Div([
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
    ])
