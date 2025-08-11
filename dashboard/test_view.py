from django.shortcuts import render


def test_chart_view(request):
    return render(request, "dashboard/test_chart.html")
