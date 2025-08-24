import plotly.express as px
import polars as pl
from plotly.graph_objects import Figure
import plotly.graph_objects as go
from dash import html
from plotly.subplots import make_subplots

def create_control_chart(
    df: pl.DataFrame,
    stats: dict,
    capability_stats: dict = None,
    active_rules: dict = None,
    settings=None,
    usl_value=None,
    lsl_value=None) -> Figure:
    """Create a control chart plot with all control stats
    
    Args:
        df: DataFrame with data
        stats: Dictionary with data-driven statistics
        active_rules: Dictionary with active rules {1: True/False, 2: True/False, ...}
                      If None, all rules are active
        settings: Dictionary with chart settings (period_type, y_axis_label, etc.)
        usl_value: Upper Specification Limit value (optional, user-configured)
        lsl_value: Lower Specification Limit value (optional, user-configured)
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
        
    # Create base plot with subplots
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05
    )
    
    # --- X-Chart (Top Subplot) ---
    
    # Add main data trace
    fig.add_trace(
        go.Scatter(x=df['index'], y=df['value'], mode='lines+markers', name='Value'),
        row=1, col=1
    )
    
    # Define and add control lines
    control_line_specs = [
        ("mean", "grey",   "Mean"), ("uwl",  "orange", "2σ"),
        ("lwl",  "orange", None),   ("uzl",  "green",  "1σ"),
        ("lzl",  "green",  None),   ("ucl",  "red",    "3σ"),
        ("lcl",  "red",    None),
    ]
    for key, color, text in control_line_specs:
        fig.add_hline(y=stats[key], line_dash="dash", line_color=color,
                      annotation=dict(font_color=color, text=text) if text else None,
                      row=1, col=1)
        
    # Add Specification Limits if provided
    if lsl_value and usl_value:
        fig.add_hline(y=lsl_value, line_dash="solid", line_color="#03244f", row=1, col=1)
        fig.add_annotation(x=0.5, xref="paper", y=lsl_value, yref="y1",
                           text="LSL", showarrow=False, xanchor="center",
                           yshift=-10, font=dict(color="#03244f"), align="center", row=1, col=1)
        fig.add_hline(y=usl_value, line_dash="solid", line_color="#03244f",
                      annotation=dict(font_color="#03244f", x=0.5, xref="paper",
                                      xanchor="center", text="USL", align="center"),
                      row=1, col=1)
    
    # Add Zone annotations
    zone_specs = [
        ("C", (stats['mean'] + stats['uzl'])/2, "green"),
        ("B", (stats['uwl'] + stats['uzl'])/2, "orange"),
        ("A", (stats['ucl'] + stats['uwl'])/2, "red"),
    ]
    for name, y_val, color in zone_specs:
        fig.add_annotation(x=df['index'].min() - 2, y=y_val, text=f"Zone {name}",
                           showarrow=False, xref="x1", yref="y1",
                           font=dict(size=12, color=color), bgcolor="rgba(255, 255, 255, 0.8)",
                           bordercolor=color, borderwidth=1, borderpad=2)

    # Highlight points with rule violations
    indices, values, hover_texts, marker_colors = [], [], [], []
    rule_cols = [f'rule_{i}' for i in range(1, 9) if active_rules.get(i, True)]
    max_rules = len(rule_cols) if rule_cols else 1

    for row in df.iter_rows(named=True):
        broken = [rule_descriptions[r] for r in rule_cols if row[r] == "Broken"]
        if broken:
            num_broken = len(broken)
            indices.append(row['index'])
            values.append(row['value'])
            hover_texts.append(f"<b>Value: {row['value']:.2f}</b><br>" + "<br>".join(broken))
            
            # Make red more intense (darker) as more rules are broken
            intensity = 1 - (num_broken - 1) / max_rules * 0.7
            red_val = int(255 * intensity)
            marker_colors.append(f'rgb({red_val}, 0, 0)')

    if indices:
        fig.add_trace(go.Scatter(
            x=indices, y=values, mode='markers',
            marker=dict(color=marker_colors, size=10, line=dict(color='black', width=1)),
            text=hover_texts, hoverinfo='text', name='Rule Violations'
        ), row=1, col=1)

    # --- mR-Chart (Bottom Subplot) ---
    
    # Add moving range trace
    fig.add_trace(
        go.Scatter(x=df['index'], y=df['moving_range'], mode='lines+markers', name='Moving Range'),
        row=2, col=1
    )
    
    # Add mR control lines
    # fig.add_hline(y=stats['mr_avg'], line_dash="dash", line_color="grey",
    #               annotation=dict(font_color="grey", text="Mean"), row=2, col=1)
    # fig.add_hline(y=stats['mr_ucl'], line_dash="dash", line_color="red",
    #               annotation=dict(font_color="red", text="UCL"), row=2, col=1)

    # --- Titles and Layout ---
    
    # Add subplot titles
    fig.add_annotation(text="<i>X-Chart: Individual Values</i>",
                       xref="paper", yref="paper", x=1, y=1.0,
                       xanchor="right", yanchor="bottom", showarrow=False, font=dict(size=14))
    fig.add_annotation(text="<i>mR-Chart: Moving Range</i>",
                       xref="paper", yref="paper", x=1, y=0.28,
                       xanchor="right", yanchor="bottom", showarrow=False, font=dict(size=14))

    # Update overall layout
    fig.update_layout(
        showlegend=False,
        hovermode='x unified',
        height=700,
        xaxis_title=None,
        xaxis2_title=settings.get('period_type', 'Observation'),
        yaxis_title=settings.get('y_axis_label', 'Individual Values'),
        yaxis2_title="Moving Range"
    )
        
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
