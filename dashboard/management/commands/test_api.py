"""
Management command to test PyBiorythm API connection.

This command tests the connection to the PyBiorythm REST API and displays
basic information about the API and available data.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.services import api_client


class Command(BaseCommand):
    help = 'Test connection to PyBiorythm API and display basic information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information including people list',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                '=' * 60 + '\n'
                'PyBiorythm API Connection Test\n'
                '=' * 60
            )
        )
        
        # Test basic connection
        self.stdout.write(f"API Base URL: {settings.PYBIORYTHM_API_BASE_URL}")
        self.stdout.write(f"API Token: {'Set' if settings.PYBIORYTHM_API_TOKEN else 'Not set'}")
        self.stdout.write("")
        
        # Get API info
        api_info = api_client.client.get_api_info()
        if not api_info:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Failed to connect to PyBiorythm API!\n"
                    "   Make sure the API server is running at the configured URL."
                )
            )
            return
        
        self.stdout.write(self.style.SUCCESS("✅ API Connection successful!"))
        self.stdout.write(f"   API Name: {api_info.get('api_name', 'Unknown')}")
        self.stdout.write(f"   Version: {api_info.get('version', 'Unknown')}")
        self.stdout.write(f"   PyBiorythm Available: {api_info.get('pybiorythm_available', False)}")
        self.stdout.write("")
        
        # Test people endpoint
        people_data = api_client.get_people_cached()
        if people_data:
            people_count = len(people_data.get('results', []))
            self.stdout.write(self.style.SUCCESS(f"✅ People endpoint working - {people_count} people found"))
            
            if options['detailed'] and people_count > 0:
                self.stdout.write("\nPeople in database:")
                for person in people_data['results'][:5]:  # Show first 5
                    self.stdout.write(
                        f"   - {person['name']} (ID: {person['id']}, "
                        f"Born: {person['birthdate']}, "
                        f"Data points: {person.get('biorhythm_data_count', 0)})"
                    )
                if people_count > 5:
                    self.stdout.write(f"   ... and {people_count - 5} more")
        else:
            self.stdout.write(self.style.WARNING("⚠️  People endpoint returned no data"))
        
        # Test global statistics
        stats = api_client.client.get_global_statistics()
        if stats:
            self.stdout.write(self.style.SUCCESS("✅ Statistics endpoint working"))
            self.stdout.write(f"   Total people: {stats.get('total_people', 0)}")
            self.stdout.write(f"   Total calculations: {stats.get('total_calculations', 0)}")
            self.stdout.write(f"   Total data points: {stats.get('total_data_points', 0)}")
            self.stdout.write(f"   Critical days: {stats.get('total_critical_days', 0)}")
        else:
            self.stdout.write(self.style.WARNING("⚠️  Statistics endpoint returned no data"))
        
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "🎉 API test completed!\n"
                f"   Dashboard URL: http://localhost:8000/\n"
                "   You can now start the dashboard server with: python manage.py runserver"
            )
        )