# PyBiorythm Django Dashboard Example

A Django web dashboard with HTMX and Plotly visualizations consuming PyBiorythm REST API data. Features real-time biorhythm charts, correlation analysis, and interactive dashboard components.

## 🌟 Features

- **Django + HTMX** for progressive enhancement without JavaScript frameworks
- **Plotly Interactive Charts** with biorhythm line charts, histograms, and correlation heatmaps
- **REST API Integration** consuming data from PyBiorythm API server
- **Real-time Updates** with HTMX for seamless user experience
- **Responsive Design** with Bootstrap styling
- **Chart Export** functionality for data visualization
- **Performance Optimized** with caching and async patterns

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Features](#features-overview)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Integration](#api-integration)
- [Charts & Visualizations](#charts--visualizations)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Quick Start

1. **Prerequisites**: Python 3.9+, [uv](https://github.com/astral-sh/uv), PyBiorythm API server running

2. **Clone and setup**:
   ```bash
   git clone https://github.com/dkdndes/pybiorythm-django-dashboard-example.git
   cd pybiorythm-django-dashboard-example
   
   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API server details
   ```

4. **Initialize and run**:
   ```bash
   uv run python manage.py migrate
   uv run python manage.py runserver 8002
   ```

5. **Access dashboard**: http://127.0.0.1:8002/

## 📦 Installation

### Prerequisites

- **Python 3.9+**
- **[uv](https://github.com/astral-sh/uv)** package manager
- **PyBiorythm API Server** (see [pybiorythm-django-api-server-example](https://github.com/dkdndes/pybiorythm-django-api-server-example))

### Installation with uv

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/dkdndes/pybiorythm-django-dashboard-example.git
cd pybiorythm-django-dashboard-example

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### Dependencies

This project uses the following key dependencies:

- **Django** 5.2.5+ - Web framework
- **django-htmx** 1.17.0+ - HTMX integration for Django
- **requests** 2.31.0+ - HTTP client for API communication
- **plotly** 5.15.0+ - Interactive visualization library
- **pandas** 2.0.0+ - Data analysis and manipulation
- **python-dateutil** 2.8.0+ - Date/time utilities

## 🏗️ Architecture

```
┌─────────────────────┐    HTTP/JSON    ┌──────────────────────┐    SQL    ┌──────────────┐
│                     │    ────────>    │                      │  ──────>  │              │
│  PyBiorythm         │                 │  Django REST API     │           │   SQLite     │
│  Dashboard          │                 │  Server (Port 8001)  │           │   Database   │
│  (Port 8002)        │    <────────    │                      │  <──────  │              │
│                     │                 │                      │           │              │
└─────────────────────┘                 └──────────────────────┘           └──────────────┘
        │                                         │
        │                                         │
    Django + HTMX                          Django REST Framework
    Plotly.js                              + PyBiorythm Library
    Bootstrap UI                           + Token Authentication
```

### Component Architecture

- **Frontend Layer**: Django templates + HTMX + Plotly.js
- **API Client**: Custom service for REST API communication
- **Chart Engine**: Server-side Plotly chart generation
- **Caching Layer**: Intelligent data caching for performance

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```bash
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# PyBiorythm API Configuration
PYBIORYTHM_API_BASE_URL=http://127.0.0.1:8001/api/
PYBIORYTHM_API_TOKEN=your-api-token-here

# Dashboard Configuration
CACHE_TIMEOUT=300
CHART_UPDATE_INTERVAL=30
```

### API Server Setup

Ensure the PyBiorythm REST API server is running:

```bash
# In a separate terminal, start the API server
cd ../pybiorythm-django-api-server-example
source .venv/bin/activate
uv run daphne biorhythm_api.asgi:application -p 8001
```

### Get API Token

Obtain an authentication token from the API server:

```bash
# Get token via API
curl -X POST http://127.0.0.1:8001/api-token-auth/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'

# Or check the API server's auth_token.txt file
```

## 💻 Usage

### Starting the Dashboard

1. **Start API Server** (in separate terminal):
   ```bash
   cd pybiorythm-django-api-server-example
   source .venv/bin/activate
   uv run daphne biorhythm_api.asgi:application -p 8001
   ```

2. **Start Dashboard**:
   ```bash
   cd pybiorythm-django-dashboard-example
   source .venv/bin/activate
   uv run python manage.py runserver 8002
   ```

3. **Access Application**:
   - Dashboard: http://127.0.0.1:8002/
   - Django Admin: http://127.0.0.1:8002/admin/

### Dashboard Features

#### 🏠 Home Dashboard
- **API Status**: Real-time connection monitoring
- **People List**: Browse and search individuals
- **Quick Stats**: Global biorhythm statistics

#### 👤 Person Dashboard
- **Biorhythm Chart**: Interactive timeline of all three cycles
- **Distribution Chart**: Histogram analysis of cycle values
- **Critical Days**: Calendar highlighting critical periods
- **Correlation Analysis**: Heatmap of cycle correlations
- **Statistics**: Comprehensive numerical analysis

#### ⚡ Interactive Features
- **Live Updates**: Charts update without page refresh using HTMX
- **Date Filtering**: Adjust time ranges for analysis
- **Export Options**: Download charts as images
- **Responsive Design**: Works on desktop and mobile

## 🔌 API Integration

### API Client Service

The dashboard uses `dashboard/services.py` for API communication:

```python
from dashboard.services import api_client

# Get person data with caching
person_data = api_client.get_person_cached(person_id=1)

# Get fresh biorhythm data
biorhythm_data = api_client.get_biorhythm_data_fresh(
    person_id=1,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    limit=1000
)

# Trigger new calculation
result = api_client.calculate_biorhythm_and_invalidate(
    person_id=1,
    days=365,
    notes="Dashboard calculation"
)
```

### Error Handling

The API client includes comprehensive error handling:

- **Connection Failures**: Graceful fallbacks
- **Authentication Errors**: Token refresh logic
- **Rate Limiting**: Retry with backoff
- **Data Validation**: Input sanitization

## 📊 Charts & Visualizations

### Biorhythm Line Chart

Interactive timeline showing physical, emotional, and intellectual cycles:

```python
def create_biorhythm_line_chart(biorhythm_data, person_name):
    fig = go.Figure()
    
    # Physical cycle (23 days)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['physical'],
        name='Physical (23 days)',
        line=dict(color='#FF6B6B', width=2),
        hovertemplate='Date: %{x}<br>Physical: %{y:.3f}<extra></extra>'
    ))
    
    # Add emotional and intellectual traces...
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)
```

### Correlation Heatmap

Displays correlations between biorhythm cycles:

```python
def create_correlation_heatmap(correlation_data):
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
        textfont={"size": 14, "color": "black"}
    ))
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)
```

### Chart Types Available

1. **Line Charts**: Time series biorhythm data
2. **Histograms**: Distribution analysis
3. **Heatmaps**: Correlation matrices
4. **Bar Charts**: Statistical summaries
5. **Scatter Plots**: Cycle relationships

## 🧪 Testing

### Run Tests

```bash
# Run all tests
uv run python manage.py test

# Run with coverage
uv run coverage run --source='.' manage.py test
uv run coverage report

# Test specific module
uv run python manage.py test dashboard.tests
```

### Test API Connection

```bash
# Test API connectivity
uv run python manage.py test_api --detailed

# Check Django configuration
uv run python manage.py check
```

### Code Quality

```bash
# Run ruff linting
uv run ruff check .

# Run ruff formatting
uv run ruff format .

# Run security checks
uv run bandit -r biorhythm_dashboard/ dashboard/ --exclude "**/migrations/**"

# Run safety checks
uv run safety check
```

## 🐳 Deployment

### Docker Deployment

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY . .
RUN uv run python manage.py migrate
RUN uv run python manage.py collectstatic --noinput

EXPOSE 8002
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8002"]
```

### Production Setup

```bash
# Use production settings
export DEBUG=False
export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
export SECRET_KEY="your-production-secret-key"

# Use production database
export DATABASE_URL="postgresql://user:pass@localhost/dashboard"

# Configure API connection
export PYBIORYTHM_API_BASE_URL="https://api.yourdomain.com/api/"
export PYBIORYTHM_API_TOKEN="production-token"

# Run with production server
uv run python manage.py runserver 0.0.0.0:8002
```

## 🔧 Development

### Project Structure

```
pybiorythm-django-dashboard-example/
├── biorhythm_dashboard/         # Django project settings
│   ├── settings.py             # Configuration
│   ├── urls.py                 # Main URL routing
│   └── asgi.py                 # ASGI configuration
├── dashboard/                   # Main application
│   ├── views.py                # Dashboard and chart views
│   ├── urls.py                 # App URL patterns
│   ├── services.py             # API client service
│   ├── plotly_utils.py         # Chart utilities
│   └── management/commands/    # Management commands
├── templates/                   # Django templates
│   ├── base.html              # Base template
│   └── dashboard/             # Dashboard templates
├── static/                     # Static files
│   ├── css/                   # Stylesheets
│   └── js/                    # JavaScript
└── .github/workflows/         # CI/CD pipelines
```

### Adding New Features

1. **New Chart Type**: Add function to `plotly_utils.py`
2. **New View**: Add to `views.py` with proper HTMX handling
3. **New Template**: Create in `templates/dashboard/`
4. **New API Endpoint**: Extend `services.py` client

### Local Development

```bash
# Install development dependencies
uv sync --extra dev

# Run development server with debug
DEBUG=True uv run python manage.py runserver 8002

# Watch for template changes
uv run python manage.py runserver --reload
```

## 🐛 Troubleshooting

### Common Issues

**API Connection Failed**:
```bash
# Check API server status
curl http://127.0.0.1:8001/api/

# Verify token
curl -H "Authorization: Token your-token" http://127.0.0.1:8001/api/people/
```

**Charts Not Loading**:
- Check browser console for JavaScript errors
- Verify Plotly.js is loaded: `window.Plotly`
- Check HTMX requests in Network tab

**No Data Available**:
- Ensure API server has biorhythm data
- Check date range filters
- Verify person exists in database

### Debug Mode

Enable detailed logging:

```bash
export DEBUG=True
export DJANGO_LOG_LEVEL=DEBUG
uv run python manage.py runserver 8002
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
uv sync --extra dev

# Run pre-commit checks
uv run ruff check .
uv run ruff format .
uv run bandit -r . --exclude "**/migrations/**"
uv run python manage.py test
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[PyBiorythm](https://github.com/dkdndes/pybiorythm)** - Core biorhythm calculation library
- **[PyBiorythm Django SQLite](https://github.com/dkdndes/pybiorythm-django-sqlite-example)** - Database integration example
- **[PyBiorythm Django API Server](https://github.com/dkdndes/pybiorythm-django-api-server-example)** - REST API server example

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/dkdndes/pybiorythm-django-dashboard-example/issues)
- **Documentation**: [README](https://github.com/dkdndes/pybiorythm-django-dashboard-example/blob/main/README.md)
- **Discussions**: [GitHub Discussions](https://github.com/dkdndes/pybiorythm-django-dashboard-example/discussions)

## 🙏 Acknowledgments

- **PyBiorythm Library** by [dkdndes](https://github.com/dkdndes)
- **Django Framework** by the Django Software Foundation
- **HTMX** by the HTMX team for modern web interactions
- **Plotly** for interactive visualization capabilities

---

**Made with ❤️ for the PyBiorythm community**