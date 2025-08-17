import plotly.express as px
import polars as pl
from plotly.graph_objects import Figure
import plotly.graph_objects as go
from dash import html

def create_control_chart(
    df: pl.DataFrame,
    stats: dict,
    capability_stats: dict = None,
    active_rules: dict = None,
    settings=None) -> Figure:
    """Create a control chart plot with all control stats
    
    Args:
        df: DataFrame with data
        stats: Dictionary with data-driven statistics
        active_rules: Dictionary with active rules {1: True/False, 2: True/False, ...}
                      If None, all rules are active
        settings: Dictionary with chart settings (period_type, y_axis_label, etc.)
    """
    # Define rule descriptions for tooltips
    rule_descriptions = {
        'rule_1': "Rule 1: Point beyond 3 sigma",
        'rule_2': "Rule 2: 9 points on same side of centerline",
        'rule_3': "Rule 3: 6 points steadily increasing/decreasing",
        'rule_4': "Rule 4: 14 points alternating up and down", 
        'rule_5': "Rule 5: 2 of 3 points in Zone A or beyond",
        'rule_6': "Rule 6: 4 of 5 points in Zone B or beyond",
        'rule_7': "Rule 7: 15 points in Zone C",
        'rule_8': "Rule 8: 8 points with none in Zone C"
    }
    
    settings = settings or {}
                
    # If active_rules is None, assume all rules are active
    if active_rules is None:
        active_rules = {i: True for i in range(1, 9)}
        
    # Create base plot
    fig = px.line(df, x='index', y='value')
    
    # Define control line specs: (stat_key, color, annotation text)
    control_line_specs = [
        ("mean", "grey",   "Mean"),
        ("uwl",  "orange", "2σ"),
        ("lwl",  "orange", None),
        ("uzl",  "green",  "1σ"),
        ("lzl",  "green",  None),
        ("ucl",  "red",    "3σ (Upper Control Limit)"),
        ("lcl",  "red",    None),
    ]

    for key, color, text in control_line_specs:
        fig.add_hline(
            y=stats[key],
            line_dash="dash",
            line_color=color,
            annotation=dict(font_color=color, text=text) if text else None
        )
    
    # Add zone annotations to the left side for top areas
    fig.add_annotation(
        x=df['index'].min() - 2,
        y=(stats['mean'] + stats['uzl'])/2,
        text="Zone C",
        showarrow=False,
        xref="x",
        yref="y",
        font=dict(size=12, color="green"),  # Match 1σ line color
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="green",
        borderwidth=1,
        borderpad=2
    )
    
    fig.add_annotation(
        x=df['index'].min() - 2,
        y=(stats['uwl'] + stats['uzl'])/2,
        text="Zone B",
        showarrow=False,
        xref="x",
        yref="y",
        font=dict(size=12, color="orange"),  # Match 2σ line color
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="orange",
        borderwidth=1,
        borderpad=2
    )
    
    fig.add_annotation(
        x=df['index'].min() - 2,
        y=(stats['ucl'] + stats['uwl'])/2,
        text="Zone A",
        showarrow=False,
        xref="x",
        yref="y",
        font=dict(size=12, color="red"),  # Match 3σ line color
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="red",
        borderwidth=1,
        borderpad=2
    )
    
    # Create arrays for scatter plot with highlighted points
    indices = []
    values = []
    hover_texts = []
    colors = []
    
    # Identify broken rules for each point
    rule_columns = [f'rule_{i}' for i in range(1, 9) if active_rules.get(i, True)]
    
    for row in df.iter_rows(named=True):
        broken_rules = []
        
        for rule in rule_columns:
            if row[rule] == "Broken":
                rule_num = rule.split('_')[1]
                broken_rules.append(f"{rule_descriptions[rule]}")
        
        if broken_rules:
            indices.append(row['index'])
            values.append(row['value'])
            # Add value to hover text with the value formatted to 2 decimal places
            value_text = f"<b>Value: {row['value']:.2f}</b>"
            hover_texts.append(value_text + "<br>" + "<br>".join(broken_rules))
            colors.append("red")  # All points with violations are red
    
    # Add highlighted points for rule violations
    if indices:
        fig.add_trace(
            go.Scatter(
                x=indices,
                y=values,
                mode='markers',
                marker=dict(
                    color=colors,
                    size=10,
                    line=dict(
                        color='black',
                        width=1
                    )
                ),
                text=hover_texts,
                hoverinfo='text',
                name='Rule Violations'
            )
        )
    
    fig.add_annotation(
        text="<i>X-chart: Time-series for individual values</i>",
        xref="paper", yref="paper",
        x=1, y=1.06,
        xanchor="right", yanchor="top",
        showarrow=False,
        font=dict(size=14)
    )
    
    fig.update_layout(
        xaxis_title=settings.get('period_type', 'Observation'),
        yaxis_title=settings.get('y_axis_label', 'Value'),
        showlegend=False,
        hovermode='closest',
        height=500)
    
    return fig

def make_stats_panel(stats, capability_stats):
    def fmt(val, precision=3):
        return f"{val:.{precision}f}" if val is not None else "N/A"

    items = [
        ("Mean", fmt(stats.get('mean'))),
        ("Std Dev", fmt(stats.get('std_dev'))),
        ("UCL", fmt(stats.get('ucl'))),
        ("LCL", fmt(stats.get('lcl'))),
        ("Range", fmt(stats.get('range'))),
        ("Min", fmt(stats.get('min'))),
        ("Max", fmt(stats.get('max'))),
        ("Sample Count", stats.get('count', 'N/A')),
        ("Cp", fmt(capability_stats.get('cp'))),
        ("Cpk", fmt(capability_stats.get('cpk'))),
    ]
    return html.Div([
        html.Div("Process Statistics", className="stats-panel-title"),
        html.Div([
            html.Div([
                html.Span(k + ":", className="stat-key"),
                html.Span(v, className="stat-value"),
            ], className="stat-row") for k, v in items
        ], className="stats-panel-grid")
    ], className="stats-panel")
