"""
Test script to debug correlation heatmap issues.
"""

import json
import pandas as pd
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder


def test_simple_heatmap():
    """Create a simple standalone heatmap for testing."""
    
    # Test correlation data
    correlation_data = [
        [1.0, 0.1, -0.2],
        [0.1, 1.0, 0.3], 
        [-0.2, 0.3, 1.0]
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_data,
        x=['Physical', 'Emotional', 'Intellectual'],
        y=['Physical', 'Emotional', 'Intellectual'],
        colorscale='RdBu',
        zmid=0,
        text=correlation_data,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
        hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Test Correlation Heatmap',
        height=400,
        width=400
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def test_real_correlation_heatmap():
    """Test with real correlation data similar to the actual function."""
    import pandas as pd
    
    # Simulate real biorhythm data
    import math
    data = []
    for i in range(100):
        days_alive = 12000 + i
        physical = math.sin(2 * math.pi * days_alive / 23)
        emotional = math.sin(2 * math.pi * days_alive / 28)
        intellectual = math.sin(2 * math.pi * days_alive / 33)
        data.append({
            'physical': physical,
            'emotional': emotional,
            'intellectual': intellectual
        })
    
    df = pd.DataFrame(data)
    correlation_matrix = df[['physical', 'emotional', 'intellectual']].corr()
    
    # Create the exact same heatmap as the main function
    fig = go.Figure()
    
    fig.add_trace(
        go.Heatmap(
            z=correlation_matrix.values,
            x=['Physical', 'Emotional', 'Intellectual'],
            y=['Physical', 'Emotional', 'Intellectual'],
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(3).values,
            texttemplate="%{text}",
            textfont={"size": 16, "color": "white"},
            hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>',
            showscale=True,
            colorbar=dict(
                title="Correlation Coefficient",
                tickmode="linear",
                tick0=-1,
                dtick=0.5
            )
        )
    )
    
    fig.update_layout(
        title='Real Data Correlation Test',
        height=400,
        width=600,
        margin=dict(l=80, r=120, t=80, b=80),
        yaxis=dict(autorange="reversed")
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)


if __name__ == "__main__":
    result = test_simple_heatmap()
    print("Test heatmap JSON generated successfully")
    print(f"JSON length: {len(result)} characters")