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
        'rule_1': "<b>Rule 1</b>: Point beyond 3 sigma",
        'rule_2': "<b>Rule 2</b>: 9 points on same side of centerline",
        'rule_3': "<b>Rule 3</b>: 6 points steadily increasing/decreasing",
        'rule_4': "<b>Rule 4</b>: 14 points alternating up and down", 
        'rule_5': "<b>Rule 5</b>: 2 of 3 points in Zone A or beyond",
        'rule_6': "<b>Rule 6</b>: 4 of 5 points in Zone B or beyond",
        'rule_7': "<b>Rule 7</b>: 15 points in Zone C",
        'rule_8': "<b>Rule 8</b>: 8 points with none in Zone C"
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
                  annotation=dict(
                  font=dict(color=color, size=9.5),
                  text=f"{text}: {round(stats[key],2)}",
                  xanchor="left",
                  xref="paper",
                  x=0.01
                  ) if text else None,
                  row=1, col=1)
        
    # Add Specification Limits if provided
    if lsl_value and usl_value:
        fig.add_hline(y=lsl_value, line_dash="solid", line_color="#03244f",
                      annotation=dict(font_color="#03244f", x=0.5, xref="paper",
                                      xanchor="center", text="LSL", align="center"),
                      row=1, col=1)
        fig.add_hline(y=usl_value, line_dash="solid", line_color="#03244f",
                      annotation=dict(font_color="#03244f", x=0.5, xref="paper",
                                      xanchor="center", text="USL", align="center"),
                      row=1, col=1)
    
    # Add Zone annotations
    zone_specs = [
        ("C", '1', stats['uzl'], "green"),
        ("B", '2', stats['uwl'], "orange"),
        ("A", '3', stats['ucl'], "red"),
    ]
    for name, sd, y_val, color in zone_specs:
        fig.add_annotation(x=df['index'].min() - 2, y=y_val, text=f"Zone {name}: up to {sd} σ",
                           showarrow=False, xref="x1", yref="y1", yshift=-13,
                           font=dict(size=11, color=color), bgcolor="rgba(255, 255, 255, 0.88)",
                           bordercolor=color, borderwidth=0.5, borderpad=1)

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
            hover_texts.append("<br>".join(broken))
            
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
    
    fig.add_hline(y=stats['mr_avg'], line_dash="dash", line_color="grey",
                  annotation=dict(font_color="grey", text=f"{stats["mr_avg"]:.2f}: Mean"), row=2, col=1)
    fig.add_hline(y=stats['mr_ucl'], line_dash="dash", line_color="red",
                  annotation=dict(font_color="red", text=f"{stats["mr_ucl"]:.2f}: Upper limit for differences between values"), row=2, col=1)

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
