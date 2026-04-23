from gcl import GCL

class Simulator:
    def __init__(self, gcl: GCL, queues: dict, routing: dict):
        self.gcl = gcl
        self.global_time = 0.0
        self.queues = queues
        self.routing = routing
        self.scheduler = []

    def next_event(self, min_t: float, max_t: float) -> float:
        r = self.gcl.next_random()
        if r == -1.0:
            return -1.0
        return min_t + (max_t - min_t) * r

    def count_time(self, event_time: float):
        delta_t = event_time - self.global_time
        if delta_t > 0:
            for q in self.queues.values():
                q.expand_state_array(q.current_capacity)
                q.accumulated_time[q.current_capacity] += delta_t
        self.global_time = event_time

    def schedule(self, event_time: float, event_type: str, queue_name: str):
        self.scheduler.append((event_time, event_type, queue_name))

    def arrival(self, event_time: float, queue_name: str, is_external: bool = True):
        self.count_time(event_time)
        q = self.queues[queue_name]

        if q.k is None or q.current_capacity < q.k:
            q.current_capacity += 1
            if q.current_capacity <= q.servers:
                t_service = self.next_event(q.min_server, q.max_server)
                if t_service != -1.0:
                    self.schedule(self.global_time + t_service, 'DEPARTURE', queue_name)
        else:
            q.lost_customers += 1

        if is_external and q.min_arrival is not None:
            t_arrival = self.next_event(q.min_arrival, q.max_arrival)
            if t_arrival != -1.0:
                self.schedule(self.global_time + t_arrival, 'ARRIVAL', queue_name)

    def departure(self, event_time: float, queue_name: str):
        self.count_time(event_time)
        q = self.queues[queue_name]

        q.current_capacity -= 1

        if q.current_capacity >= q.servers:
            t_service = self.next_event(q.min_server, q.max_server)
            if t_service != -1.0:
                self.schedule(self.global_time + t_service, 'DEPARTURE', queue_name)

        if queue_name in self.routing and len(self.routing[queue_name]) > 0:
            r = self.gcl.next_random()
            if r == -1.0: return

            cumulative_prob = 0.0
            target_queue = None

            for route in self.routing[queue_name]:
                cumulative_prob += route.probability
                if r <= cumulative_prob:
                    target_queue = route.target
                    break

            if target_queue:
                self.arrival(event_time, target_queue, is_external=False)

    def run(self, initial_arrivals: dict):
        for q_name, q in self.queues.items():
            if q.min_arrival is not None and q_name in initial_arrivals:
                self.schedule(initial_arrivals[q_name], 'ARRIVAL', q_name)

        while self.gcl.remaining > 0 and len(self.scheduler) > 0:
            self.scheduler.sort(key=lambda x: x[0])
            current_event_time, event_type, q_name = self.scheduler.pop(0)

            if event_type == 'ARRIVAL':
                self.arrival(current_event_time, q_name, is_external=True)
            elif event_type == 'DEPARTURE':
                self.departure(current_event_time, q_name)
