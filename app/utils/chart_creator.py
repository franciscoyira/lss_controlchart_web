import plotly.express as px
import polars as pl
from plotly.graph_objects import Figure
import plotly.graph_objects as go


def create_control_chart(df: pl.DataFrame, stats: dict, active_rules: dict = None) -> Figure:
    """Create a control chart plot with all control stats
    
    Args:
        df: DataFrame with data
        stats: Dictionary with control stats
        stats: Dictionary with descriptive statistics
        active_rules: Dictionary with active rules {1: True/False, 2: True/False, ...}
                      If None, all rules are active
    """
    # If active_rules is None, assume all rules are active
    if active_rules is None:
        active_rules = {i: True for i in range(1, 9)}
        
    # Create base plot
    fig = px.line(df, x='index', y='value', title='Control Chart Plot')
    
    # Add control limit lines
    fig.add_hline(y=stats['mean'], line_dash="dash", line_color="grey", annotation_text="Mean", annotation=dict(font_color="grey"))
    fig.add_hline(y=stats['uwl'], line_dash="dash", line_color="orange", annotation_text="2σ", annotation=dict(font_color="orange"))
    fig.add_hline(y=stats['lwl'], line_dash="dash", line_color="orange")
    fig.add_hline(y=stats['uzl'], line_dash="dash", line_color="green", annotation_text="1σ", annotation=dict(font_color="green"))
    fig.add_hline(y=stats['lzl'], line_dash="dash", line_color="green")
    fig.add_hline(y=stats['ucl'], line_dash="dash", line_color="red", annotation_text="3σ", annotation=dict(font_color="red"))
    fig.add_hline(y=stats['lcl'], line_dash="dash", line_color="red")
    
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
    
    # Update layout to add more height for annotations
    fig.update_layout(
        xaxis_title="Observation",
        yaxis_title="Value",
        showlegend=False,
        hovermode='closest',
        height=700,  # Increase height to accommodate stats better
        margin=dict(b=200)  # Increase bottom margin for stats
    )
    
    # Add descriptive statistics at the bottom
    stat_text = "<br>".join([
        f"<b>Process Statistics:</b>",
        f"Mean: {stats['mean']:.3f}",
        f"Std Dev: {stats['stddev']:.3f}",
        f"UCL: {stats['ucl']:.3f}, LCL: {stats['lcl']:.3f}",
        f"Range: {stats['range']:.3f} (Min: {stats['min']:.3f}, Max: {stats['max']:.3f})",
        f"Sample Count: {stats['count']}",
        f"Process Capability (Cp): {stats['CP']:.3f}"
    ])
    
    fig.add_annotation(
        xref='paper',
        yref='paper',
        x=0.5,
        y=-0.45,  # Move the annotation lower
        text=stat_text,
        showarrow=False,
        font=dict(size=12),
        align='center',
        bordercolor='black',
        borderwidth=1,
        borderpad=4,
        bgcolor='white',
        opacity=0.8
    )
    
    return fig
