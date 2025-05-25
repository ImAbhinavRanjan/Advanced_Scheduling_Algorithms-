import sys
import os
from collections import deque
from .utils.metrics import average_times

# Process class is expected to have: pid, arrival, burst, remaining, completion, waiting, turnaround, timeline

def anrr(processes):
    time = 0
    queue = []
    arrival_index = 0
    n = len(processes)
    completed = 0
    context_switches = 0
    processes.sort(key=lambda p: p.arrival)
    prev_pid = None

    def dynamic_quantum(q):
        return sum(p.remaining for p in q) // len(q) if q else 2

    while completed < n:
        while arrival_index < n and processes[arrival_index].arrival <= time:
            if processes[arrival_index] not in queue:
                queue.append(processes[arrival_index])
            arrival_index += 1

        if queue:
            quantum = dynamic_quantum(queue)
            current = queue.pop(0)
            if prev_pid != current.pid:
                context_switches += 1
            prev_pid = current.pid

            exec_time = min(current.remaining, quantum)
            current.timeline.append((time, exec_time))
            time += exec_time
            current.remaining -= exec_time

            while arrival_index < n and processes[arrival_index].arrival <= time:
                if processes[arrival_index] not in queue:
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

    return average_times(processes) + (context_switches,)

def amrr(processes):
    time = 0
    queue = []
    arrival_index = 0
    n = len(processes)
    completed = 0
    base_quantum = 2
    context_switches = 0
    processes.sort(key=lambda p: p.arrival)
    prev_pid = None

    while completed < n:
        while arrival_index < n and processes[arrival_index].arrival <= time:
            if processes[arrival_index] not in queue:
                queue.append(processes[arrival_index])
            arrival_index += 1

        if queue:
            current = queue.pop(0)
            if prev_pid != current.pid:
                context_switches += 1
            prev_pid = current.pid

            quantum = base_quantum + (current.remaining // 2)
            exec_time = min(current.remaining, quantum)
            current.timeline.append((time, exec_time))
            time += exec_time
            current.remaining -= exec_time

            while arrival_index < n and processes[arrival_index].arrival <= time:
                if processes[arrival_index] not in queue:
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

    return average_times(processes) + (context_switches,)

def round_robin(processes, quantum):
    time = 0
    queue = []
    arrival_index = 0
    n = len(processes)
    completed = 0
    context_switches = 0
    processes.sort(key=lambda p: p.arrival)
    prev_pid = None

    while completed < n:
        while arrival_index < n and processes[arrival_index].arrival <= time:
            if processes[arrival_index] not in queue:
                queue.append(processes[arrival_index])
            arrival_index += 1

        if queue:
            current = queue.pop(0)
            if prev_pid != current.pid:
                context_switches += 1
            prev_pid = current.pid

            exec_time = min(current.remaining, quantum)
            current.timeline.append((time, exec_time))
            time += exec_time
            current.remaining -= exec_time

            while arrival_index < n and processes[arrival_index].arrival <= time:
                if processes[arrival_index] not in queue:
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

    return average_times(processes) + (context_switches,)

def mmrra(processes):
    time = 0
    arrival_index = 0
    completed = 0
    n = len(processes)
    context_switches = 0
    priority_levels = [deque(), deque(), deque()]  # Low, Medium, High
    wait_times = {}
    processes.sort(key=lambda p: p.arrival)
    prev_pid = None
    AGING_THRESHOLD = 5

    def get_priority(p):
        if p.burst <= 4:
            return 2
        elif p.burst <= 8:
            return 1
        else:
            return 0

    def get_quantum(priority):
        return [2, 3, 4][priority]

    while completed < n:
        while arrival_index < n and processes[arrival_index].arrival <= time:
            p = processes[arrival_index]
            prio = get_priority(p)
            priority_levels[prio].append(p)
            wait_times[p.pid] = 0
            arrival_index += 1

        # Apply aging
        for prio in range(2):
            new_queue = deque()
            while priority_levels[prio]:
                p = priority_levels[prio].popleft()
                wait_times[p.pid] += 1
                if wait_times[p.pid] >= AGING_THRESHOLD:
                    priority_levels[prio + 1].append(p)
                    wait_times[p.pid] = 0
                else:
                    new_queue.append(p)
            priority_levels[prio] = new_queue

        current = None
        for level in reversed(priority_levels):
            if level:
                current = level.popleft()
                break

        if current:
            if prev_pid != current.pid:
                context_switches += 1
            prev_pid = current.pid

            priority = get_priority(current)
            quantum = get_quantum(priority)
            exec_time = min(current.remaining, quantum)
            current.timeline.append((time, exec_time))
            time += exec_time
            current.remaining -= exec_time

            while arrival_index < n and processes[arrival_index].arrival <= time:
                p = processes[arrival_index]
                prio = get_priority(p)
                priority_levels[prio].append(p)
                wait_times[p.pid] = 0
                arrival_index += 1

            if current.remaining > 0:
                priority_levels[priority].append(current)
                wait_times[current.pid] = 0
            else:
                current.completion = time
                completed += 1
        else:
            time += 1

    for p in processes:
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst

    return average_times(processes) + (context_switches,) 