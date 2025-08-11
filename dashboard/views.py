"""
Dashboard views for PyBiorythm visualization dashboard.

Provides Django views that consume the PyBiorythm REST API and present
interactive Plotly visualizations using HTMX for dynamic updates.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.conf import settings

from .services import api_client
from .plotly_utils import (
    create_biorhythm_line_chart,
    create_cycle_distribution_chart,
    create_critical_days_calendar,
    create_cycle_phase_chart,
    create_correlation_chart,
    create_statistics_summary_chart,
    create_empty_chart,
    get_chart_config
)

logger = logging.getLogger(__name__)


def dashboard_home(request: HttpRequest) -> HttpResponse:
    """
    Main dashboard view showing overview and person selection.
    
    Displays API status, available people, and navigation to detailed views.
    """
    context = {
        'page_title': 'PyBiorythm Dashboard',
        'api_connected': False,
        'people': [],
        'global_stats': None,
        'error_message': None
    }
    
    # Check API connection
    api_info = api_client.client.get_api_info()
    if api_info:
        context['api_connected'] = True
        context['api_info'] = api_info
    else:
        context['error_message'] = "Unable to connect to PyBiorythm API. Please check the server is running."
    
    # Get people list
    if context['api_connected']:
        people_data = api_client.get_people_cached()
        if people_data and 'results' in people_data:
            context['people'] = people_data['results']
        
        # Get global statistics
        global_stats = api_client.client.get_global_statistics()
        if global_stats:
            context['global_stats'] = global_stats
    
    return render(request, 'dashboard/home.html', context)


def person_dashboard(request: HttpRequest, person_id: int) -> HttpResponse:
    """
    Detailed dashboard view for a specific person's biorhythm data.
    
    Shows comprehensive visualizations and statistics for the selected person.
    """
    context = {
        'person_id': person_id,
        'person': None,
        'biorhythm_data': None,
        'statistics': None,
        'error_message': None,
        'chart_config': get_chart_config()
    }
    
    # Get person details
    person_data = api_client.get_person_cached(person_id)
    if not person_data:
        context['error_message'] = f"Person with ID {person_id} not found."
        return render(request, 'dashboard/person_dashboard.html', context)
    
    context['person'] = person_data
    
    # Get biorhythm data (last 365 days by default)
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    # Allow date range override from query parameters
    if request.GET.get('start_date'):
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if request.GET.get('end_date'):
        try:
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    biorhythm_response = api_client.get_biorhythm_data_fresh(
        person_id, start_date=start_date, end_date=end_date, limit=1000
    )
    
    if biorhythm_response and 'biorhythm_data' in biorhythm_response:
        context['biorhythm_data'] = biorhythm_response['biorhythm_data']
        context['data_info'] = {
            'start_date': start_date,
            'end_date': end_date,
            'data_points': biorhythm_response.get('data_points', 0),
            'date_range': biorhythm_response.get('date_range', {})
        }
    
    # Get statistics
    statistics = api_client.get_person_statistics_cached(person_id)
    if statistics:
        context['statistics'] = statistics
    
    return render(request, 'dashboard/person_dashboard.html', context)


@require_http_methods(["GET"])
@never_cache
def chart_biorhythm_line(request: HttpRequest, person_id: int) -> JsonResponse:
    """
    HTMX endpoint for biorhythm line chart data.
    
    Returns Plotly chart data for the main biorhythm cycles visualization.
    """
    try:
        # Get date range from query parameters
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        if request.GET.get('start_date'):
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        if request.GET.get('end_date'):
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        
        # Get person and biorhythm data
        person_data = api_client.get_person_cached(person_id)
        if not person_data:
            return JsonResponse({
                'chart_data': create_empty_chart("Person not found"),
                'config': get_chart_config()
            })
        
        biorhythm_response = api_client.get_biorhythm_data_fresh(
            person_id, start_date=start_date, end_date=end_date, limit=1000
        )
        
        if biorhythm_response and 'biorhythm_data' in biorhythm_response:
            chart_data = create_biorhythm_line_chart(
                biorhythm_response['biorhythm_data'],
                person_data['name']
            )
        else:
            chart_data = create_empty_chart("No biorhythm data available")
        
        return JsonResponse({
            'chart_data': chart_data,
            'config': get_chart_config()
        })
        
    except Exception as e:
        logger.error(f"Error generating line chart for person {person_id}: {e}")
        return JsonResponse({
            'chart_data': create_empty_chart("Error loading chart data"),
            'config': get_chart_config()
        })


@require_http_methods(["GET"])
@never_cache
def chart_distribution(request: HttpRequest, person_id: int) -> JsonResponse:
    """
    HTMX endpoint for cycle distribution chart data.
    """
    try:
        person_data = api_client.get_person_cached(person_id)
        if not person_data:
            return JsonResponse({
                'chart_data': create_empty_chart("Person not found"),
                'config': get_chart_config()
            })
        
        # Get all available data for distribution analysis
        biorhythm_response = api_client.get_biorhythm_data_fresh(person_id, limit=5000)
        
        if biorhythm_response and 'biorhythm_data' in biorhythm_response:
            chart_data = create_cycle_distribution_chart(
                biorhythm_response['biorhythm_data'],
                person_data['name']
            )
        else:
            chart_data = create_empty_chart("No biorhythm data available")
        
        return JsonResponse({
            'chart_data': chart_data,
            'config': get_chart_config()
        })
        
    except Exception as e:
        logger.error(f"Error generating distribution chart for person {person_id}: {e}")
        return JsonResponse({
            'chart_data': create_empty_chart("Error loading chart data"),
            'config': get_chart_config()
        })


@require_http_methods(["GET"])
@never_cache
def chart_critical_days(request: HttpRequest, person_id: int) -> JsonResponse:
    """
    HTMX endpoint for critical days calendar chart data.
    """
    try:
        person_data = api_client.get_person_cached(person_id)
        if not person_data:
            return JsonResponse({
                'chart_data': create_empty_chart("Person not found"),
                'config': get_chart_config()
            })
        
        # Get last year of data for calendar view
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        biorhythm_response = api_client.get_biorhythm_data_fresh(
            person_id, start_date=start_date, end_date=end_date, limit=1000
        )
        
        if biorhythm_response and 'biorhythm_data' in biorhythm_response:
            chart_data = create_critical_days_calendar(
                biorhythm_response['biorhythm_data'],
                person_data['name']
            )
        else:
            chart_data = create_empty_chart("No biorhythm data available")
        
        return JsonResponse({
            'chart_data': chart_data,
            'config': get_chart_config()
        })
        
    except Exception as e:
        logger.error(f"Error generating critical days chart for person {person_id}: {e}")
        return JsonResponse({
            'chart_data': create_empty_chart("Error loading chart data"),
            'config': get_chart_config()
        })


@require_http_methods(["GET"])
@never_cache
def chart_cycle_phases(request: HttpRequest, person_id: int) -> JsonResponse:
    """
    HTMX endpoint for current cycle phases polar chart data.
    """
    try:
        person_data = api_client.get_person_cached(person_id)
        if not person_data:
            return JsonResponse({
                'chart_data': create_empty_chart("Person not found"),
                'config': get_chart_config()
            })
        
        # Get recent data for current phase calculation
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        biorhythm_response = api_client.get_biorhythm_data_fresh(
            person_id, start_date=start_date, end_date=end_date, limit=10
        )
        
        if biorhythm_response and 'biorhythm_data' in biorhythm_response:
            chart_data = create_cycle_phase_chart(
                biorhythm_response['biorhythm_data'],
                person_data['name']
            )
        else:
            chart_data = create_empty_chart("No recent biorhythm data available")
        
        return JsonResponse({
            'chart_data': chart_data,
            'config': get_chart_config()
        })
        
    except Exception as e:
        logger.error(f"Error generating phase chart for person {person_id}: {e}")
        return JsonResponse({
            'chart_data': create_empty_chart("Error loading chart data"),
            'config': get_chart_config()
        })


@require_http_methods(["GET"])
@never_cache
def chart_correlation(request: HttpRequest, person_id: int) -> JsonResponse:
    """
    HTMX endpoint for correlation chart data.
    """
    try:
        person_data = api_client.get_person_cached(person_id)
        if not person_data:
            logger.error(f"Person {person_id} not found")
            return JsonResponse({
                'chart_data': create_empty_chart("Person not found"),
                'config': get_chart_config()
            })
        
        # Get all available data for correlation analysis
        biorhythm_response = api_client.get_biorhythm_data_fresh(person_id, limit=5000)
        logger.info(f"Biorhythm response for person {person_id}: {biorhythm_response is not None}")
        
        if biorhythm_response and 'biorhythm_data' in biorhythm_response:
            biorhythm_data = biorhythm_response['biorhythm_data']
            logger.info(f"Got {len(biorhythm_data)} biorhythm data points for correlation")
            
            chart_data = create_correlation_chart(
                biorhythm_data,
                person_data['name']
            )
            logger.info("Correlation chart created successfully")
        else:
            logger.error(f"No biorhythm data in response: {biorhythm_response}")
            chart_data = create_empty_chart("No biorhythm data available")
        
        return JsonResponse({
            'chart_data': chart_data,
            'config': get_chart_config()
        })
        
    except Exception as e:
        logger.error(f"Error generating correlation chart for person {person_id}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return JsonResponse({
            'chart_data': create_empty_chart(f"Error: {str(e)}"),
            'config': get_chart_config()
        })


@require_http_methods(["GET"])
@never_cache
def chart_statistics(request: HttpRequest, person_id: int) -> JsonResponse:
    """
    HTMX endpoint for statistics summary chart data.
    """
    try:
        person_data = api_client.get_person_cached(person_id)
        if not person_data:
            return JsonResponse({
                'chart_data': create_empty_chart("Person not found"),
                'config': get_chart_config()
            })
        
        statistics = api_client.get_person_statistics_cached(person_id)
        
        if statistics:
            chart_data = create_statistics_summary_chart(statistics, person_data['name'])
        else:
            chart_data = create_empty_chart("No statistics available")
        
        return JsonResponse({
            'chart_data': chart_data,
            'config': get_chart_config()
        })
        
    except Exception as e:
        logger.error(f"Error generating statistics chart for person {person_id}: {e}")
        return JsonResponse({
            'chart_data': create_empty_chart("Error loading chart data"),
            'config': get_chart_config()
        })


@require_http_methods(["POST"])
def calculate_biorhythm(request: HttpRequest, person_id: int) -> HttpResponse:
    """
    HTMX endpoint to trigger new biorhythm calculation.
    """
    try:
        days = int(request.POST.get('days', 365))
        notes = request.POST.get('notes', '')
        
        result = api_client.calculate_biorhythm_and_invalidate(
            person_id, days=days, notes=notes
        )
        
        if result:
            messages.success(request, f"Successfully calculated {days} days of biorhythm data.")
            return render(request, 'dashboard/calculation_success.html', {
                'calculation': result.get('calculation', {}),
                'data_points_created': result.get('data_points_created', 0)
            })
        else:
            messages.error(request, "Failed to calculate biorhythm data.")
            return render(request, 'dashboard/calculation_error.html', {
                'error': "Calculation failed"
            })
            
    except Exception as e:
        logger.error(f"Error calculating biorhythm for person {person_id}: {e}")
        messages.error(request, f"Error: {str(e)}")
        return render(request, 'dashboard/calculation_error.html', {
            'error': str(e)
        })


@require_http_methods(["GET"])
def api_status(request: HttpRequest) -> JsonResponse:
    """
    HTMX endpoint to check API connection status.
    """
    api_info = api_client.client.get_api_info()
    return JsonResponse({
        'connected': bool(api_info),
        'info': api_info or {},
        'timestamp': datetime.now().isoformat()
    })


@require_http_methods(["GET"])
def people_list_partial(request: HttpRequest) -> HttpResponse:
    """
    HTMX endpoint to reload people list.
    """
    search = request.GET.get('search', '')
    
    if search:
        people_data = api_client.client.get_people(search=search)
    else:
        people_data = api_client.get_people_cached()
    
    people = people_data.get('results', []) if people_data else []
    
    return render(request, 'dashboard/partials/people_list.html', {
        'people': people,
        'search_query': search
    })


@require_http_methods(["GET"])
def person_info_partial(request: HttpRequest, person_id: int) -> HttpResponse:
    """
    HTMX endpoint to get person info card.
    """
    person_data = api_client.get_person_cached(person_id)
    statistics = api_client.get_person_statistics_cached(person_id)
    
    return render(request, 'dashboard/partials/person_info.html', {
        'person': person_data,
        'statistics': statistics
    })


@require_http_methods(["GET"])
def test_correlation_view(request: HttpRequest) -> JsonResponse:
    """
    Test endpoint for correlation heatmap debugging.
    """
    from .test_correlation import test_real_correlation_heatmap
    
    chart_data = test_real_correlation_heatmap()
    
    return JsonResponse({
        'chart_data': chart_data,
        'config': get_chart_config()
    })


def test_correlation_page(request: HttpRequest) -> HttpResponse:
    """Test page for correlation heatmap."""
    return render(request, 'dashboard/test_correlation.html')


@require_http_methods(["GET"]) 
def test_simple_correlation_view(request: HttpRequest) -> JsonResponse:
    """Test simplified correlation chart without annotations."""
    try:
        # Get real data from API
        biorhythm_response = api_client.get_biorhythm_data_fresh(1, limit=1000)
        
        if biorhythm_response and 'biorhythm_data' in biorhythm_response:
            biorhythm_data = biorhythm_response['biorhythm_data']
            
            # Create simplified chart without annotations
            import pandas as pd
            import plotly.graph_objects as go
            from plotly.utils import PlotlyJSONEncoder
            import json
            
            df = pd.DataFrame(biorhythm_data)
            cycles = ['physical', 'emotional', 'intellectual']
            correlation_matrix = df[cycles].corr()
            
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
                    showscale=True
                )
            )
            
            fig.update_layout(
                title='Simplified Correlation Heatmap - Real Data',
                height=400,
                width=500,
                margin=dict(l=80, r=80, t=80, b=80),
                yaxis=dict(autorange="reversed")
            )
            
            chart_data = json.dumps(fig, cls=PlotlyJSONEncoder)
        else:
            chart_data = create_empty_chart("No data available")
            
        return JsonResponse({
            'chart_data': chart_data,
            'config': get_chart_config()
        })
        
    except Exception as e:
        return JsonResponse({
            'chart_data': create_empty_chart(f"Error: {str(e)}"),
            'config': get_chart_config()
        })


@require_http_methods(["GET"]) 
def debug_correlation_data(request: HttpRequest) -> JsonResponse:
    """Debug endpoint to see what correlation data looks like."""
    try:
        biorhythm_response = api_client.get_biorhythm_data_fresh(1, limit=100)
        
        if biorhythm_response and 'biorhythm_data' in biorhythm_response:
            biorhythm_data = biorhythm_response['biorhythm_data']
            
            import pandas as pd
            df = pd.DataFrame(biorhythm_data)
            cycles = ['physical', 'emotional', 'intellectual']
            correlation_matrix = df[cycles].corr()
            
            # Return debug info
            return JsonResponse({
                'data_points': len(biorhythm_data),
                'sample_data': biorhythm_data[:3] if biorhythm_data else [],
                'correlation_values': correlation_matrix.values.tolist(),
                'has_nan': bool(correlation_matrix.isna().any().any()),
                'physical_range': [float(df['physical'].min()), float(df['physical'].max())],
                'emotional_range': [float(df['emotional'].min()), float(df['emotional'].max())],
                'intellectual_range': [float(df['intellectual'].min()), float(df['intellectual'].max())],
                'correlation_matrix_dict': {
                    'physical_emotional': float(correlation_matrix.loc['physical', 'emotional']),
                    'physical_intellectual': float(correlation_matrix.loc['physical', 'intellectual']),
                    'emotional_intellectual': float(correlation_matrix.loc['emotional', 'intellectual'])
                }
            })
        else:
            return JsonResponse({'error': 'No biorhythm data available'})
            
    except Exception as e:
        return JsonResponse({'error': str(e)})


@require_http_methods(["GET"]) 
def test_exact_correlation(request: HttpRequest) -> JsonResponse:
    """Test with the exact correlation values we found."""
    import plotly.graph_objects as go
    from plotly.utils import PlotlyJSONEncoder
    import json
    
    # Use the exact correlation matrix from debug
    correlation_data = [
        [1.0, 0.238, -0.048],
        [0.238, 1.0, 0.380],
        [-0.048, 0.380, 1.0]
    ]
    
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
    
    fig.update_layout(
        title='Test Exact Correlation Values',
        height=400,
        width=500
    )
    
    chart_data = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return JsonResponse({
        'chart_data': chart_data,
        'config': get_chart_config()
    })
