from threading import Thread, Event
from collections import defaultdict
import matplotlib.pyplot as plt
from time import time, sleep
from rich.progress import *
from worker import Worker
from queue import Queue
import networkx as nx
import pickle
import os

start = str(time())

if not os.path.exists('runs'):
    os.mkdir('runs')

os.mkdir(os.path.join('runs', start))

with_labels = False
num_threads = 64
err_filepth = os.path.join('runs', start, 'failed.txt')

def fetch():
    global adjacency, completed, paths

    worker = Worker()

    while True:
        if event.isSet():
            return

        path = queue.get()

        (hrefs, title), success = worker.fetch(path, save_errors = True, filepath = err_filepth, verbose = True)

        if success:
            for href in hrefs:
                if href not in paths:
                    queue.put(href)

            adjacency[path].update(hrefs)
            paths.update(hrefs)

        queue.task_done()
        completed += 1

worker = Worker()
adjacency = defaultdict(set)
completed = 0

paths = set()
queue = Queue()
event = Event()

queue.put('Main_Page')

threads = []

for i in range(num_threads):
    thread = Thread(target = fetch, daemon = True)
    thread.start()
    threads.append(thread)

pbar = [
    "[progress.description]{task.description}",
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
    "{task.completed} of {task.total}",
    TimeElapsedColumn(),
    TimeRemainingColumn(),
    SpinnerColumn()
]

while queue.empty():
    sleep(0.1)

with Progress(*pbar) as progress:
    task = progress.add_task('Mapping Wikipedia', total = completed)

    while completed < 100 or not queue.empty():
        total = len(paths)
        progress.update(task, total = total, completed = completed, refresh = True)
        sleep(1)

event.set()
print ('Waiting for threads to terminate...')
while any(thread.is_alive() for thread in threads):
    sleep(0.1)

print ('Generating graph...')
graph = nx.from_dict_of_lists(adjacency)

filepath = os.path.join('runs', start, 'graph.txt')
print (f'Saving graph to {filepath}...')
with open(filepath, 'wb') as f:
    pickle.dump(graph, f, protocol = pickle.HIGHEST_PROTOCOL)
