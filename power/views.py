import json

from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import TimePoint
from .forms import SelectionForm

def home(request):
    return render(request, 'power/home.html')

def form_view(request):
    selected_devices = []
    all_results = {}

    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            time_span = form.cleaned_data['time_span']
            selected_devices = form.cleaned_data['devices']
            interval = form.cleaned_data['interval']
            difference = form.cleaned_data['difference'] 
            show_graph = form.cleaned_data['show_graph']


            time_mapping = {
                "1 day": timedelta(days=1),
                "1 week": timedelta(weeks=1),
                "2 weeks": timedelta(days=14),
                "3 weeks": timedelta(days=21),
                "1 month": timedelta(days=30),
                "3 months": timedelta(days=90),
                "6 months": timedelta(days=180),
                "1 year": timedelta(days=365),
            }
            time_delta = time_mapping.get(time_span, timedelta(days=7))
            start_time = timezone.now() - time_delta

            interval_mapping = {
                '10min': timedelta(minutes=10),
                '1h': timedelta(hours=1),
                '6h': timedelta(hours=6),
                '1d': timedelta(days=1),
            }
            interval_delta = interval_mapping.get(interval, timedelta(hours=1)) 


            filtered_data = TimePoint.objects.filter(time__gte=start_time).order_by('time')

            for device in selected_devices:
                results = []
                previous_value = None
                last_included_time = None

                for entry in filtered_data:
                    value = getattr(entry, device, None)
                    if value is None:
                        continue

                    if last_included_time is None or (entry.time - last_included_time) >= interval_delta:
                        if difference:
                            if previous_value is not None:
                                diff_value = value - previous_value
                                results.append({
                                    "time": entry.time,
                                    "value": diff_value,
                                })
                            else:
                                results.append({
                                    "time": entry.time,
                                    "value": 0,
                                })
                            previous_value = value
                        else:
                            results.append({
                                "time": entry.time,
                                "value": value,
                            })

                        last_included_time = entry.time

                all_results[device] = results
                    
            results_js = json.dumps(all_results, default=str)

            return render(request, 'power/form_result.html', {
                'time_span': time_span,
                'selected_devices': selected_devices,
                'difference': difference,
                'all_results': all_results,
                'results_js': results_js,
                'show_graph': show_graph,
            })
    else:
        form = SelectionForm()

    return render(request, 'power/form_page.html', {'form': form})


