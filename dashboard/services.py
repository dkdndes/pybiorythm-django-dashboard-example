"""
API client services for connecting to PyBiorythm REST API.

This module provides a client interface for communicating with the Django REST API
server that manages biorhythm data and calculations.
"""

import requests
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PyBiorythmAPIClient:
    """
    Client for interacting with PyBiorythm REST API.
    
    Handles authentication, data fetching, and error handling for all
    API interactions with the biorhythm data server.
    """
    
    def __init__(self):
        self.base_url = settings.PYBIORYTHM_API_BASE_URL.rstrip('/')
        self.token = settings.PYBIORYTHM_API_TOKEN
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                'Authorization': f'Token {self.token}',
                'Content-Type': 'application/json',
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request to API with error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {e}")
            return None
    
    def get_api_info(self) -> Optional[Dict[str, Any]]:
        """Get API information and health status."""
        return self._make_request('GET', '')
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate with the API and get token."""
        data = {'username': username, 'password': password}
        response = self._make_request('POST', 'auth/token/', json=data)
        
        if response and 'token' in response:
            self.token = response['token']
            self.session.headers.update({
                'Authorization': f'Token {self.token}'
            })
        
        return response
    
    def get_people(self, search: Optional[str] = None, limit: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get list of people with optional search and pagination."""
        params = {}
        if search:
            params['search'] = search
        if limit:
            params['page_size'] = limit
            
        return self._make_request('GET', 'people/', params=params)
    
    def get_person(self, person_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific person."""
        return self._make_request('GET', f'people/{person_id}/')
    
    def get_person_biorhythm_data(
        self, 
        person_id: int, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get biorhythm data for a specific person with filtering."""
        params = {}
        if start_date:
            params['start_date'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['end_date'] = end_date.strftime('%Y-%m-%d')
        if limit:
            params['limit'] = limit
            
        return self._make_request('GET', f'people/{person_id}/biorhythm_data/', params=params)
    
    def get_person_statistics(self, person_id: int) -> Optional[Dict[str, Any]]:
        """Get statistical summary for a person's biorhythm data."""
        return self._make_request('GET', f'people/{person_id}/statistics/')
    
    def calculate_biorhythm(
        self,
        person_id: int,
        days: int = 365,
        target_date: Optional[date] = None,
        notes: str = ''
    ) -> Optional[Dict[str, Any]]:
        """Trigger new biorhythm calculation for a person."""
        data = {
            'person_id': person_id,
            'days': days,
            'notes': notes
        }
        if target_date:
            data['target_date'] = target_date.strftime('%Y-%m-%d')
            
        return self._make_request('POST', 'calculations/calculate/', json=data)
    
    def get_calculations(self, person_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get list of calculations with optional person filtering."""
        params = {}
        if person_id:
            params['person_id'] = person_id
            
        return self._make_request('GET', 'calculations/', params=params)
    
    def get_global_statistics(self) -> Optional[Dict[str, Any]]:
        """Get global statistics about all biorhythm data."""
        return self._make_request('GET', 'statistics/')


class CachedAPIClient:
    """
    Wrapper around PyBiorythmAPIClient with caching for improved performance.
    
    Provides intelligent caching for frequently accessed data like person lists
    and statistics while ensuring fresh data for real-time calculations.
    """
    
    def __init__(self):
        self.client = PyBiorythmAPIClient()
        self.cache_timeout = 300  # 5 minutes default
    
    def get_people_cached(self, cache_key: str = 'api_people_list') -> Optional[Dict[str, Any]]:
        """Get people list with caching."""
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
            
        data = self.client.get_people()
        if data:
            cache.set(cache_key, data, self.cache_timeout)
        return data
    
    def get_person_cached(self, person_id: int) -> Optional[Dict[str, Any]]:
        """Get person details with caching."""
        cache_key = f'api_person_{person_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
            
        data = self.client.get_person(person_id)
        if data:
            cache.set(cache_key, data, self.cache_timeout)
        return data
    
    def get_person_statistics_cached(self, person_id: int) -> Optional[Dict[str, Any]]:
        """Get person statistics with caching."""
        cache_key = f'api_person_stats_{person_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
            
        data = self.client.get_person_statistics(person_id)
        if data:
            cache.set(cache_key, data, self.cache_timeout * 2)  # Cache longer for stats
        return data
    
    def invalidate_person_cache(self, person_id: int):
        """Invalidate all cached data for a specific person."""
        cache_keys = [
            f'api_person_{person_id}',
            f'api_person_stats_{person_id}',
            'api_people_list'
        ]
        cache.delete_many(cache_keys)
    
    def get_biorhythm_data_fresh(
        self, 
        person_id: int, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get biorhythm data without caching (always fresh)."""
        return self.client.get_person_biorhythm_data(
            person_id, start_date, end_date, limit
        )
    
    def calculate_biorhythm_and_invalidate(
        self,
        person_id: int,
        days: int = 365,
        target_date: Optional[date] = None,
        notes: str = ''
    ) -> Optional[Dict[str, Any]]:
        """Calculate biorhythm and invalidate related caches."""
        result = self.client.calculate_biorhythm(person_id, days, target_date, notes)
        if result:
            self.invalidate_person_cache(person_id)
        return result


# Global instance for use throughout the application
api_client = CachedAPIClient()