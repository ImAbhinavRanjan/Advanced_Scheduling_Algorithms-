from django.http import JsonResponse
from django.shortcuts import render

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.completion = 0
        self.waiting = 0
        self.turnaround = 0

def round_robin(processes, quantum):
    time = 0
    queue = []
    arrival_index = 0
    n = len(processes)
    completed = 0

    processes.sort(key=lambda p: p.arrival)

    while completed < n:
        while arrival_index < n and processes[arrival_index].arrival <= time:
            queue.append(processes[arrival_index])
            arrival_index += 1

        if queue:
            current = queue.pop(0)
            exec_time = min(current.remaining, quantum)
            time += exec_time
            current.remaining -= exec_time

            while arrival_index < n and processes[arrival_index].arrival <= time:
                queue.append(processes[arrival_index])
                arrival_index += 1

            if current.remaining > 0:
                queue.append(current)
            else:
                current.completion = time
                completed += 1
        else:
            time += 1

    for p in processes:
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst

    avg_waiting = sum(p.waiting for p in processes) / n
    avg_turnaround = sum(p.turnaround for p in processes) / n

    return avg_waiting, avg_turnaround

def mmrra(processes):
    time = 0
    queue = []
    processes.sort(key=lambda p: p.arrival)
    arrival_index = 0
    completed = 0
    n = len(processes)
    priority_levels = [[], [], []]  # Low, Medium, High

    def get_priority(p):
        if p.burst <= 4:
            return 2  # High
        elif p.burst <= 8:
            return 1  # Medium
        else:
            return 0  # Low

    def get_quantum(priority):
        return [4, 3, 2][priority]

    while completed < n:
        while arrival_index < n and processes[arrival_index].arrival <= time:
            p = processes[arrival_index]
            priority = get_priority(p)
            priority_levels[priority].append(p)
            arrival_index += 1

        current = None
        for level in reversed(priority_levels):
            if level:
                current = level.pop(0)
                break

        if current:
            priority = get_priority(current)
            quantum = get_quantum(priority)
            execute_time = min(current.remaining, quantum)
            time += execute_time
            current.remaining -= execute_time

            while arrival_index < n and processes[arrival_index].arrival <= time:
                p = processes[arrival_index]
                priority = get_priority(p)
                priority_levels[priority].append(p)
                arrival_index += 1

            if current.remaining > 0:
                priority_levels[priority].append(current)
            else:
                current.completion = time
                completed += 1
        else:
            time += 1

    for p in processes:
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst

    avg_waiting = sum(p.waiting for p in processes) / n
    avg_turnaround = sum(p.turnaround for p in processes) / n

    return avg_waiting, avg_turnaround

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

            process_list_rr = [Process(p.pid, p.arrival, p.burst) for p in processes_data]
            process_list_mmrra = [Process(p.pid, p.arrival, p.burst) for p in processes_data]

            quantum = 4
            rr_avg_wait, rr_avg_tat = round_robin(process_list_rr, quantum)
            mmrra_avg_wait, mmrra_avg_tat = mmrra(process_list_mmrra)

            return JsonResponse({
                'rr_avg_wait': round(rr_avg_wait, 2),
                'rr_avg_tat': round(rr_avg_tat, 2),
                'mmrra_avg_wait': round(mmrra_avg_wait, 2),
                'mmrra_avg_tat': round(mmrra_avg_tat, 2),
            })
        except ValueError:
            return JsonResponse({'error': 'Invalid input. Please enter valid numbers.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)