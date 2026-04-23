import yaml
import sys
from gcl import GCL
from queue import Queue
from simulator import Simulator
from route import Route

def parse_yaml_config(filepath: str):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    yaml_lines = [line for line in lines if not line.startswith('!PARAMETERS')]
    model = yaml.safe_load("".join(yaml_lines))
    
    arrivals = model.get('arrivals', {})
    
    queues = {}
    for q_name, q_data in model.get('queues', {}).items():
        queues[q_name] = Queue(
            name=q_name,
            servers=q_data.get('servers', 1),
            capacity=q_data.get('capacity', None),
            min_arrival=q_data.get('minArrival', None),
            max_arrival=q_data.get('maxArrival', None),
            min_service=q_data.get('minService', 0.0),
            max_service=q_data.get('maxService', 0.0)
        )
        
    routing = {}
    for route in model.get('network', []):
        src = route['source']
        target = route['target']
        prob = route['probability']
        if src not in routing:
            routing[src] = []
        routing[src].append(Route(target, prob))
        
    seeds = model.get('seeds', [9013])
    rnd_per_seed = model.get('rndnumbersPerSeed', 100000)
    
    return arrivals, queues, routing, seeds, rnd_per_seed

def fmt(value: float, decimals: int = 4) -> str:
    return f"{value:.{decimals}f}".replace('.', ',')

def print_simulation_report(queues: dict, total_global_time: float, num_seeds: int):
    print("=========================================================")
    print("=================    END OF SIMULATION   ================")
    print("=========================================================")
    print()
    print("=========================================================")
    print("======================    REPORT   ======================")
    print("=========================================================")
    
    for q_name, q in queues.items():
        cap_str = f"/{q.k}" if q.k is not None else ""
        queue_info = f"G/G/{q.servers}{cap_str}"
        print("*********************************************************")
        print(f"Queue:   {q_name} ({queue_info})")
        if q.min_arrival is not None:
            print(f"Arrival: {q.min_arrival} ... {q.max_arrival}")
        print(f"Service: {q.min_server} ... {q.max_server}")
        print("*********************************************************")
        
        print(f"   {'State':<20}{'Time':<19}{'Probability':<11}")
        for state, acc_time in enumerate(q.global_accumulated_time):
            prob = (acc_time / total_global_time) * 100 if total_global_time > 0 else 0
            
            state_str = str(state).rjust(7)
            time_str = fmt(acc_time).rjust(12)
            prob_str = f"{fmt(prob, 2)}%".rjust(6)
            
            print(f"{state_str}         {time_str}                {prob_str}")
            
        print()
        print(f"Number of losses: {q.global_lost_customers}")
        print()
        
    avg_time = total_global_time / num_seeds if num_seeds > 0 else 0.0
    print("=========================================================")
    print(f"Simulation average time: {fmt(avg_time)}")
    print("=========================================================")

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py model.yml")
        sys.exit(1)
        
    model_path = sys.argv[1]
    
    tempo_chegada_inicial = 2.0

    arrivals, queues, routing, seeds, rnd_per_seed = parse_yaml_config(model_path)
    
    total_global_time = 0.0
    
    for i, seed in enumerate(seeds):
        print(f"Simulation: #{i+1}")
        print(f"...simulating with random numbers (seed '{seed}')...")
        
        gcl = GCL(seed=int(seed), limit=rnd_per_seed)
        
        for q in queues.values():
            q.reset_queue()
            
        simulator = Simulator(gcl, queues, routing)
        simulator.run(default_first_arrival=tempo_chegada_inicial, explicit_arrivals=arrivals)
        
        for q in queues.values():
            q.accumulate_stats()
            
        total_global_time += simulator.global_time
        
    print_simulation_report(queues, total_global_time, len(seeds))

if __name__ == '__main__':
    main()
