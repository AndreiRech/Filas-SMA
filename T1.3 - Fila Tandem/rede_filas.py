# M6 - REDE DE FILAS
# Alunos: Andrei Rech, Carlos Moraes, Eduardo Wolf e Eduardo de Bastiani

class GCL:
    def __init__(self, seed=9013, a=709, c=5678341, m=2**23, limit=100000):
        self.xi = seed
        self.a = a
        self.c = c
        self.m = m
        self.remaining = limit

    def next_random(self) -> float:        
        if self.remaining <= 0:
            return -1.0
            
        self.xi = (self.a * self.xi + self.c) % self.m
        self.remaining -= 1
        return self.xi / self.m

class Queue:
    def __init__(self, name: str, k: int, servers: int, min_arrival: float = None, max_arrival: float = None, min_server: float = 0.0, max_server: float = 0.0):
        self.name = name
        self.k = k
        self.servers = servers

        self.min_arrival = min_arrival
        self.max_arrival = max_arrival
        self.min_server = min_server
        self.max_server = max_server

        self.current_capacity = 0
        self.accumulated_time = [0.0] * (k + 1)
        self.lost_customers = 0

class Simulator:
    def __init__(self, gcl: GCL):
        self.gcl = gcl
        self.global_time = 0.0
        self.queues = {}
        self.routing = {}
        self.scheduler = [] # (tempo , evento [1 = entrada | 0 = saida], nome_fila)

    def add_queue(self, queue: Queue):
        self.queues[queue.name] = queue

    def add_routing(self, source: str, target: str, probability: float):
        if source not in self.routing:
            self.routing[source] = []
        
        self.routing[source].append((target, probability))

    def next_event(self, min_t: float, max_t: float) -> float:
        r = self.gcl.next_random()

        if r == -1.0:
            return -1.0
        
        return min_t + (max_t - min_t) * r
        
    def count_time(self, event_time: float):        
        delta_t = event_time - self.global_time

        if delta_t > 0:
            for q in self.queues.values():
                q.accumulated_time[q.current_capacity] += delta_t
        
        self.global_time = event_time

    def schedule(self, event_time: float, event_type: str, queue_name: str):
        self.scheduler.append((event_time, event_type, queue_name))

    def arrival(self, event_time: float, queue_name: str, is_external: bool = True):
        self.count_time(event_time)
        q = self.queues[queue_name]
        
        if q.current_capacity < q.k:
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
            
            for dest, prob in self.routing[queue_name]:
                cumulative_prob += prob

                if r <= cumulative_prob:
                    target_queue = dest
                    break
            
            if target_queue:
                self.arrival(event_time, target_queue, is_external=False)

    def run(self, first_arrival: float = 1.5):
        for q_name, q in self.queues.items():
            if q.min_arrival is not None:
                self.schedule(first_arrival, 'ARRIVAL', q_name)

        while self.gcl.remaining > 0 and len(self.scheduler) > 0:
            self.scheduler.sort(key=lambda x: x[0])
            
            current_event_time, event_type, q_name = self.scheduler.pop(0)
            
            if event_type == 'ARRIVAL':
                self.arrival(current_event_time, q_name, is_external=True)
            elif event_type == 'DEPARTURE':
                self.departure(current_event_time, q_name)

        self.print_result()

    def print_result(self):
        print("-" * 55)
        print(f"RELATÓRIO DA SIMULAÇÃO")
        print(f"Tempo total: {self.global_time:.4f}")
        print("-" * 55)

        for q_name, q in self.queues.items():
            print(f"\n{q_name}")
            print(f"Clientes perdidos: {q.lost_customers}")
            print("-" * 55)
            print(f"{'Estado (K)':<12} | {'Tempo acumulado':<18} | {'Probabilidade':<13}")
            print("-" * 55)
            for i in range(q.k + 1):
                probability = (q.accumulated_time[i] / self.global_time) * 100 if self.global_time > 0 else 0
                print(f"  {i:<10} |   {q.accumulated_time[i]:<16.4f} |   {probability:.2f}%")
            print("-" * 55)

def main():
    gcl = GCL(seed=9013, a=709, c=5678341, m=2**23, limit=100000)
    
    simulator = Simulator(gcl)

    fila_1 = Queue(name="Fila 1", servers=2, k=3, min_arrival=1.0, max_arrival=4.0, min_server=3.0, max_server=4.0)
    fila_2 = Queue(name="Fila 2", servers=1, k=5, min_arrival=None, max_arrival=None, min_server=2.0, max_server=3.0)

    simulator.add_queue(fila_1)
    simulator.add_queue(fila_2)

    simulator.add_routing(source="Fila 1", target="Fila 2", probability=1.0)

    simulator.run(first_arrival=1.5)

if __name__ == "__main__":
    main()