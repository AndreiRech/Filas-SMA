class Queue:
    def __init__(self, name: str, servers: int, capacity: int = None, min_arrival: float = None, max_arrival: float = None, min_service: float = 0.0, max_service: float = 0.0):
        self.name = name
        self.k = capacity
        self.servers = servers
        self.min_arrival = min_arrival
        self.max_arrival = max_arrival
        self.min_server = min_service
        self.max_server = max_service

        self.current_capacity = 0
        self.accumulated_time = [0.0]
        self.lost_customers = 0

        self.global_accumulated_time = [0.0]
        self.global_lost_customers = 0

    def expand_state_array(self, state: int):
        while len(self.accumulated_time) <= state:
            self.accumulated_time.append(0.0)
        while len(self.global_accumulated_time) <= state:
            self.global_accumulated_time.append(0.0)

    def reset_queue(self):
        self.current_capacity = 0
        self.accumulated_time = [0.0] * len(self.accumulated_time)
        self.lost_customers = 0

    def accumulate_stats(self):
        self.global_lost_customers += self.lost_customers
        for i, t in enumerate(self.accumulated_time):
            if i < len(self.global_accumulated_time):
                self.global_accumulated_time[i] += t
            else:
                self.global_accumulated_time.append(t)
