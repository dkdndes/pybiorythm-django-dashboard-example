"""
Plotly visualization utilities for biorhythm data.

This module creates interactive Plotly charts based on the visualizations
from the PyBiorythm notebooks, adapted for web display with HTMX integration.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from datetime import datetime, date, timedelta
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from django.conf import settings


def create_biorhythm_line_chart(biorhythm_data: List[Dict], person_name: str) -> str:
    """
    Create interactive line chart showing biorhythm cycles over time.
    
    Args:
        biorhythm_data: List of biorhythm data points from API
        person_name: Name of the person for chart title
        
    Returns:
        JSON string representation of the Plotly figure
    """
    if not biorhythm_data:
        return create_empty_chart("No biorhythm data available")
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(biorhythm_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date to ensure proper order
    df = df.sort_values('date')
    
    # Generate continuous daily data for smooth curves
    # Create a complete date range
    date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
    
    # For missing dates, calculate biorhythm values mathematically
    import math
    
    # Get the first entry to extract birthdate info
    if len(biorhythm_data) > 0:
        # Calculate days_alive for each date based on the pattern
        first_entry = biorhythm_data[0]
        first_date = pd.to_datetime(first_entry['date'])
        first_days_alive = first_entry['days_alive']
        
        # Generate complete dataset
        complete_data = []
        for single_date in date_range:
            # Calculate days alive for this date
            days_diff = (single_date - first_date).days
            days_alive = first_days_alive + days_diff
            
            # Calculate biorhythm values using the standard formulas
            physical = math.sin(2 * math.pi * days_alive / 23)
            emotional = math.sin(2 * math.pi * days_alive / 28)
            intellectual = math.sin(2 * math.pi * days_alive / 33)
            
            complete_data.append({
                'date': single_date,
                'physical': physical,
                'emotional': emotional,
                'intellectual': intellectual
            })
        
        # Create DataFrame from complete calculated data
        df = pd.DataFrame(complete_data)
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Physical cycle (23-day cycle)
    fig.add_trace(go.Scatter(
        x=df['date'].tolist(),
        y=df['physical'].tolist(),
        mode='lines',
        name='Physical (23 days)',
        line=dict(color='#FF6B6B', width=2),
        hovertemplate='<b>Physical</b><br>Date: %{x}<br>Value: %{y:.3f}<extra></extra>'
    ))
    
    # Emotional cycle (28-day cycle) 
    fig.add_trace(go.Scatter(
        x=df['date'].tolist(),
        y=df['emotional'].tolist(),
        mode='lines',
        name='Emotional (28 days)',
        line=dict(color='#4ECDC4', width=2),
        hovertemplate='<b>Emotional</b><br>Date: %{x}<br>Value: %{y:.3f}<extra></extra>'
    ))
    
    # Intellectual cycle (33-day cycle)
    fig.add_trace(go.Scatter(
        x=df['date'].tolist(),
        y=df['intellectual'].tolist(),
        mode='lines',
        name='Intellectual (33 days)',
        line=dict(color='#45B7D1', width=2),
        hovertemplate='<b>Intellectual</b><br>Date: %{x}<br>Value: %{y:.3f}<extra></extra>'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Mark critical days from original data
    original_df = pd.DataFrame(biorhythm_data)
    original_df['date'] = pd.to_datetime(original_df['date'])
    
    critical_dates = original_df[
        (original_df['is_physical_critical'] == True) | 
        (original_df['is_emotional_critical'] == True) | 
        (original_df['is_intellectual_critical'] == True)
    ]['date']
    
    if not critical_dates.empty:
        fig.add_trace(go.Scatter(
            x=critical_dates.tolist(),
            y=[0] * len(critical_dates),
            mode='markers',
            name='Critical Days',
            marker=dict(
                symbol='diamond',
                size=8,
                color='red',
                line=dict(color='darkred', width=1)
            ),
            hovertemplate='<b>Critical Day</b><br>Date: %{x}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'Biorhythm Cycles - {person_name}',
            x=0.5,
            font=dict(size=20)
        ),
        xaxis_title='Date',
        yaxis_title='Cycle Value',
        yaxis=dict(range=[-1.1, 1.1]),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
    )
    
    # Configure Plotly settings
    config = settings.PLOTLY_CONFIG.copy()
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def create_cycle_distribution_chart(biorhythm_data: List[Dict], person_name: str) -> str:
    """
    Create histogram showing distribution of cycle values.
    
    Args:
        biorhythm_data: List of biorhythm data points from API
        person_name: Name of the person for chart title
        
    Returns:
        JSON string representation of the Plotly figure
    """
    if not biorhythm_data:
        return create_empty_chart("No biorhythm data available")
    
    df = pd.DataFrame(biorhythm_data)
    
    # Create subplots for each cycle
    fig = go.Figure()
    
    cycles = [
        ('physical', 'Physical', '#FF6B6B'),
        ('emotional', 'Emotional', '#4ECDC4'),
        ('intellectual', 'Intellectual', '#45B7D1')
    ]
    
    for cycle, label, color in cycles:
        fig.add_trace(go.Histogram(
            x=df[cycle].tolist(),
            name=label,
            nbinsx=20,
            opacity=0.7,
            marker_color=color,
            hovertemplate=f'<b>{label}</b><br>Range: %{{x}}<br>Count: %{{y}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=f'Biorhythm Cycle Distribution - {person_name}',
            x=0.5,
            font=dict(size=20)
        ),
        xaxis_title='Cycle Value',
        yaxis_title='Frequency',
        barmode='overlay',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def create_critical_days_calendar(biorhythm_data: List[Dict], person_name: str) -> str:
    """
    Create calendar heatmap showing critical days over time.
    
    Args:
        biorhythm_data: List of biorhythm data points from API
        person_name: Name of the person for chart title
        
    Returns:
        JSON string representation of the Plotly figure
    """
    if not biorhythm_data:
        return create_empty_chart("No biorhythm data available")
    
    df = pd.DataFrame(biorhythm_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Count critical days by type
    df['critical_count'] = (
        df['is_physical_critical'].astype(int) +
        df['is_emotional_critical'].astype(int) +
        df['is_intellectual_critical'].astype(int)
    )
    
    # Create calendar data
    df['year'] = df['date'].dt.year
    df['day_of_year'] = df['date'].dt.dayofyear
    df['weekday'] = df['date'].dt.day_name()
    df['week'] = df['date'].dt.isocalendar().week
    
    # Create heatmap
    fig = go.Figure(data=go.Scatter(
        x=df['week'],
        y=df['weekday'],
        mode='markers',
        marker=dict(
            size=df['critical_count'] * 10 + 5,
            color=df['critical_count'],
            colorscale='Reds',
            cmin=0,
            cmax=3,
            showscale=True,
            colorbar=dict(
                title="Critical Days",
                tickvals=[0, 1, 2, 3],
                ticktext=["None", "1 Cycle", "2 Cycles", "3 Cycles"]
            )
        ),
        text=df['date'].dt.strftime('%Y-%m-%d'),
        hovertemplate='<b>%{text}</b><br>Critical Cycles: %{marker.color}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'Critical Days Calendar - {person_name}',
            x=0.5,
            font=dict(size=20)
        ),
        xaxis_title='Week of Year',
        yaxis_title='Day of Week',
        yaxis=dict(
            categoryorder='array',
            categoryarray=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def create_cycle_phase_chart(biorhythm_data: List[Dict], person_name: str) -> str:
    """
    Create polar chart showing current cycle phases.
    
    Args:
        biorhythm_data: List of biorhythm data points from API
        person_name: Name of the person for chart title
        
    Returns:
        JSON string representation of the Plotly figure
    """
    if not biorhythm_data:
        return create_empty_chart("No biorhythm data available")
    
    # Get latest data point
    latest_data = biorhythm_data[-1] if biorhythm_data else {}
    
    if not latest_data:
        return create_empty_chart("No current biorhythm data available")
    
    # Calculate cycle phases (in degrees)
    days_alive = latest_data.get('days_alive', 0)
    physical_phase = (days_alive % 23) / 23 * 360
    emotional_phase = (days_alive % 28) / 28 * 360
    intellectual_phase = (days_alive % 33) / 33 * 360
    
    # Create polar chart
    fig = go.Figure()
    
    cycles = [
        ('Physical', physical_phase, latest_data.get('physical', 0), '#FF6B6B'),
        ('Emotional', emotional_phase, latest_data.get('emotional', 0), '#4ECDC4'),
        ('Intellectual', intellectual_phase, latest_data.get('intellectual', 0), '#45B7D1')
    ]
    
    for cycle_name, phase, value, color in cycles:
        fig.add_trace(go.Scatterpolar(
            r=[0, abs(value)],
            theta=[phase, phase],
            mode='lines+markers',
            name=cycle_name,
            line=dict(color=color, width=4),
            marker=dict(size=[5, 15], color=color),
            hovertemplate=f'<b>{cycle_name}</b><br>Phase: {phase:.1f}°<br>Value: {value:.3f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=f'Current Cycle Phases - {person_name}',
            x=0.5,
            font=dict(size=20)
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            ),
            angularaxis=dict(
                direction='clockwise',
                period=360
            )
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        showlegend=True
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def create_correlation_chart(biorhythm_data: List[Dict], person_name: str) -> str:
    """
    Create correlation matrix heatmap showing relationships between biorhythm cycles.
    
    Args:
        biorhythm_data: List of biorhythm data points from API
        person_name: Name of the person for chart title
        
    Returns:
        JSON string representation of the Plotly figure
    """
    if not biorhythm_data:
        return create_empty_chart("No biorhythm data available")
    
    df = pd.DataFrame(biorhythm_data)
    
    # Calculate correlation matrix
    cycles = ['physical', 'emotional', 'intellectual']
    correlation_matrix = df[cycles].corr()
    
    # Debug: ensure we have valid correlation data
    correlation_matrix = correlation_matrix.fillna(0)  # Replace NaN with 0
    
    # Convert to simple list format like the working test
    correlation_data = correlation_matrix.values.tolist()
    
    # Create simple heatmap exactly like the working test
    fig = go.Figure(data=go.Heatmap(
        z=correlation_data,
        x=['Physical', 'Emotional', 'Intellectual'],
        y=['Physical', 'Emotional', 'Intellectual'],
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=correlation_data,
        texttemplate="%{text:.3f}",
        textfont={"size": 14, "color": "black"},
        hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>',
        showscale=True
    ))
    
    # Add correlation statistics as annotations
    corr_pe = correlation_matrix.loc['physical', 'emotional']
    corr_pi = correlation_matrix.loc['physical', 'intellectual']  
    corr_ei = correlation_matrix.loc['emotional', 'intellectual']
    
    # Determine correlation strength descriptions
    def corr_strength(corr_val):
        abs_corr = abs(corr_val)
        if abs_corr >= 0.7:
            return "Strong"
        elif abs_corr >= 0.3:
            return "Moderate"
        else:
            return "Weak"
    
    # Add summary statistics annotation (positioned below the heatmap)
    stats_text = (
        f"<b>Correlation Analysis:</b> "
        f"Physical↔Emotional: {corr_pe:.3f} ({corr_strength(corr_pe)}), "
        f"Physical↔Intellectual: {corr_pi:.3f} ({corr_strength(corr_pi)}), "
        f"Emotional↔Intellectual: {corr_ei:.3f} ({corr_strength(corr_ei)}) "
        f"| Data points: {len(df)}"
    )
    
    fig.add_annotation(
        text=stats_text,
        xref="paper", yref="paper",
        x=0.5, y=-0.12,
        showarrow=False,
        bgcolor="rgba(248,249,250,0.95)",
        bordercolor="gray",
        borderwidth=1,
        align="center",
        font=dict(size=10),
        xanchor="center"
    )
    
    # Update layout (exactly like the working test)
    fig.update_layout(
        title=f'Biorhythm Cycle Correlation Matrix - {person_name}',
        height=400,
        width=500
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def create_statistics_summary_chart(statistics: Dict[str, Any], person_name: str) -> str:
    """
    Create comprehensive statistics chart showing multiple biorhythm metrics.
    
    Args:
        statistics: Statistics data from API
        person_name: Name of the person for chart title
        
    Returns:
        JSON string representation of the Plotly figure
    """
    if not statistics or 'statistics' not in statistics:
        return create_empty_chart("No statistics data available")
    
    stats = statistics['statistics']
    cycle_averages = stats.get('cycle_averages', {})
    critical_days = stats.get('critical_days', {})
    breakdown = critical_days.get('breakdown', {})
    
    # Create comprehensive metrics for display
    fig = go.Figure()
    
    # Critical Days by Cycle (more meaningful than tiny averages)
    critical_names = ['Physical Critical', 'Emotional Critical', 'Intellectual Critical']
    critical_values = [
        breakdown.get('physical', 0),
        breakdown.get('emotional', 0), 
        breakdown.get('intellectual', 0)
    ]
    critical_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    fig.add_trace(go.Bar(
        x=critical_names,
        y=critical_values,
        marker_color=critical_colors,
        text=[f'{v}' for v in critical_values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Critical Days: %{y}<extra></extra>',
        name='Critical Days'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'Critical Days Analysis - {person_name}',
            x=0.5,
            font=dict(size=20)
        ),
        xaxis_title='Cycle Type',
        yaxis_title='Number of Critical Days',
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        showlegend=False
    )
    
    # Add comprehensive annotation with all statistics
    total_days = stats.get('total_data_points', 0)
    total_critical = critical_days.get('total', 0)
    percentage = critical_days.get('percentage', 0)
    date_range = stats.get('date_range', {})
    days_covered = date_range.get('days_covered', 0)
    
    annotation_text = (
        f"<b>Data Summary:</b><br>"
        f"• Total Data Points: {total_days}<br>"
        f"• Date Coverage: {days_covered} days<br>"
        f"• Total Critical Days: {total_critical} ({percentage:.1f}%)<br>"
        f"• Cycle Averages: P={cycle_averages.get('physical', 0):.3f}, "
        f"E={cycle_averages.get('emotional', 0):.3f}, "
        f"I={cycle_averages.get('intellectual', 0):.3f}"
    )
    
    fig.add_annotation(
        text=annotation_text,
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        bgcolor="rgba(248,249,250,0.9)",
        bordercolor="gray",
        borderwidth=1,
        align="left",
        font=dict(size=10)
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def create_empty_chart(message: str = "No data available") -> str:
    """
    Create an empty chart with a message.
    
    Args:
        message: Message to display
        
    Returns:
        JSON string representation of the Plotly figure
    """
    fig = go.Figure()
    
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray"),
        bgcolor="white"
    )
    
    fig.update_layout(
        title=dict(
            text='Biorhythm Visualization',
            x=0.5,
            font=dict(size=20)
        ),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        showlegend=False
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def get_chart_config() -> Dict[str, Any]:
    """Get Plotly configuration for all charts."""
    return settings.PLOTLY_CONFIG.copy()