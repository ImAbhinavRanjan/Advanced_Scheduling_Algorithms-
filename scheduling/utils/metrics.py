def average_times(processes):
    n = len(processes)
    avg_waiting = sum(p.waiting for p in processes) / n
    avg_turnaround = sum(p.turnaround for p in processes) / n
    return round(avg_waiting, 2), round(avg_turnaround, 2) 