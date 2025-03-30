from dash import html, dcc

def create_rule_boxes():
    """Create the rule boxes component with illustrations and descriptions"""
    rules = [
        {
            'number': 1,
            'title': 'Point Beyond 3 Sigma',
            'description': 'A single point falls outside the 3-sigma control limits',
            'icon': '/assets/rule1.svg'
        },
        {
            'number': 2,
            'title': 'Nine Points Same Side',
            'description': 'Nine consecutive points fall on the same side of the centerline',
            'icon': '/assets/rule2.svg'
        },
        {
            'number': 3,
            'title': 'Six Points Trending',
            'description': 'Six points in a row steadily increasing or decreasing',
            'icon': '/assets/rule3.svg'
        },
        {
            'number': 4,
            'title': 'Fourteen Points Alternating',
            'description': 'Fourteen points in a row alternating up and down',
            'icon': '/assets/rule4.svg'
        },
        {
            'number': 5,
            'title': 'Two of Three in Zone A',
            'description': 'Two out of three consecutive points fall in Zone A or beyond',
            'icon': '/assets/rule5.svg'
        },
        {
            'number': 6,
            'title': 'Four of Five in Zone B',
            'description': 'Four out of five consecutive points fall in Zone B or beyond',
            'icon': '/assets/rule6.svg'
        },
        {
            'number': 7,
            'title': 'Fifteen Points in Zone C',
            'description': 'Fifteen consecutive points fall within Zone C',
            'icon': '/assets/rule7.svg'
        },
        {
            'number': 8,
            'title': 'Eight Points Outside Zone C',
            'description': 'Eight consecutive points fall outside Zone C',
            'icon': '/assets/rule8.svg'
        }
    ]

    rule_boxes = []
    for rule in rules:
        rule_box = html.Div([
            html.Img(src=rule['icon'], className='rule-icon'),
            html.Div([
                html.H4(f"Rule {rule['number']}: {rule['title']}", className='rule-title'),
                html.P(rule['description'], className='rule-description')
            ], className='rule-content'),
            html.Div([
                dcc.Checklist(
                    options=[{'label': '', 'value': f'rule-{rule["number"]}'}],
                    value=[],
                    id=f'rule-check-{rule["number"]}',
                    className='rule-checkbox'
                )
            ], className='rule-checkbox-container')
        ], className='rule-box')
        rule_boxes.append(rule_box)

    return html.Div(rule_boxes, className='rule-boxes-grid') 