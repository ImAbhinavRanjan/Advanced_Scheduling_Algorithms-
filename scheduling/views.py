from django.http import JsonResponse
from django.shortcuts import render
from .algorithms import round_robin, mmrra, anrr, amrr

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.completion = 0
        self.waiting = 0
        self.turnaround = 0
        self.timeline = []

def index(request):
    return render(request, 'index.html')

def process_scheduling(request):
    if request.method == 'POST':
        try:
            processes_data = []
            i = 1
            while f'pid_{i}' in request.POST:
                pid = int(request.POST[f'pid_{i}'])
                arrival = int(request.POST[f'arrival_{i}'])
                burst = int(request.POST[f'burst_{i}'])
                if pid < 1 or arrival < 0 or burst < 1:
                    return JsonResponse({'error': 'Invalid input: PID ≥ 1, Arrival ≥ 0, Burst ≥ 1.'}, status=400)
                processes_data.append(Process(pid, arrival, burst))
                i += 1

            if not processes_data:
                return JsonResponse({'error': 'No processes provided.'}, status=400)

            # Prepare process lists for each algorithm
            process_list_rr = [Process(p.pid, p.arrival, p.burst) for p in processes_data]
            process_list_mmrra = [Process(p.pid, p.arrival, p.burst) for p in processes_data]
            process_list_anrr = [Process(p.pid, p.arrival, p.burst) for p in processes_data]
            process_list_amrr = [Process(p.pid, p.arrival, p.burst) for p in processes_data]

            quantum = 4
            rr_avg_wait, rr_avg_tat, rr_context = round_robin(process_list_rr, quantum)
            mmrra_avg_wait, mmrra_avg_tat, mmrra_context = mmrra(process_list_mmrra)
            anrr_avg_wait, anrr_avg_tat, anrr_context = anrr(process_list_anrr)
            amrr_avg_wait, amrr_avg_tat, amrr_context = amrr(process_list_amrr)

            return JsonResponse({
                'rr_avg_wait': rr_avg_wait,
                'rr_avg_tat': rr_avg_tat,
                'rr_context': rr_context,
                'mmrra_avg_wait': mmrra_avg_wait,
                'mmrra_avg_tat': mmrra_avg_tat,
                'mmrra_context': mmrra_context,
                'anrr_avg_wait': anrr_avg_wait,
                'anrr_avg_tat': anrr_avg_tat,
                'anrr_context': anrr_context,
                'amrr_avg_wait': amrr_avg_wait,
                'amrr_avg_tat': amrr_avg_tat,
                'amrr_context': amrr_context,
            })
        except ValueError:
            return JsonResponse({'error': 'Invalid input. Please enter valid numbers.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)