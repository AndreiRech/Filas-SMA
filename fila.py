# M4 - FILA SIMPLES
# Alunos: Andrei Rech, Carlos Moraes, Eduardo Wolf e Eduardo de Bastiani

# Variáveis globais
xi = 9013
a = 709
c = 5678341
M = 2**23
remaining_values = 100000

k = 5
servers_number = 2
min_arrival, max_arrival = 2.0, 5.0
min_server, max_server = 3.0, 5.0
first_arrival = 2.0

global_time = 0.0
current_capacity = 0
accumulated_time = [0.0] * (k + 1)
scheduler = [] # (tempo , evento [1 = entrada | 0 = saida])
lost_customers = 0

# - Funções auxiliares
def verify_params(a: int, c: int, M: int, x0: int, amount: int) -> bool:
    # teoricamente essa não seria precisa mas vai que alguém coloca um número inválido ne
    if M <= 0:
        print("'M' must be a positive number")
        return False
    if a <= 0 or a >= M:
        print("'a' must be positive and less than 'M'")
        return False
    if c < 0 or c >= M:
        print("'c' must be positive and less than 'M'")
        return False
    if x0 < 0 or x0 >= M:
        print("'x0' must be positive and less than 'M'")
        return False
    if amount <= 0:
        print("The amount of numbers must be positive")
        return False
    return True

def count_time(event_time: float):
    global global_time, accumulated_time, current_capacity
    
    delta_t = event_time - global_time
    accumulated_time[current_capacity] += delta_t
    global_time = event_time

def print_result():
    print(f"Tempo total: {global_time:.4f}")
    print(f"Clientes perdidos: {lost_customers}")
    print("-" * 55)
    print(f"{'Estado (K)':<12} | {'Tempo acumulado':<18} | {'Probabilidade':<13}")
    print("-" * 55)
    for i in range(k + 1):
        probability = (accumulated_time[i] / global_time) * 100 if global_time > 0 else 0
        print(f"  {i:<10} |   {accumulated_time[i]:<16.4f} |   {probability:.2f}%")
    print("-" * 55)

# - Funções de geração de números aleatórios e definição de eventos
def next_random() -> float:
    global xi, a, c, M, remaining_values
    
    if remaining_values <= 0:
        return -1.0
        
    xi = (a * xi + c) % M
    remaining_values -= 1
    
    return xi / M

def next_event(min_t: float, max_t: float) -> float:
    r = next_random()

    if r == -1.0:
        return -1.0
    
    return min_t + (max_t - min_t) * r

# - Funções de Chegada / Saída
def arrival(event_time: float):
    global current_capacity, k, scheduler, servers_number, lost_customers
    
    count_time(event_time)
    
    if current_capacity < k:
        current_capacity += 1
        
        if current_capacity <= servers_number:
            t_service = next_event(min_server, max_server)
            if t_service != -1.0:
                scheduler.append((global_time + t_service, 0))
    else:
        lost_customers += 1
                
    t_arrival = next_event(min_arrival, max_arrival)

    if t_arrival != -1.0:
        scheduler.append((global_time + t_arrival, 1))

def departure(event_time: float):
    global current_capacity, scheduler, servers_number
    
    count_time(event_time)
    current_capacity -= 1
    
    if current_capacity >= servers_number:
        t_service = next_event(min_server, max_server)
        if t_service != -1.0:
            scheduler.append((global_time + t_service, 0))

def main():
    global scheduler, remaining_values, accumulated_time, global_time, lost_customers, first_arrival
    
    if not verify_params(a, c, M, xi, remaining_values): return

    scheduler.append((first_arrival, 1))

    while remaining_values > 0 and len(scheduler) > 0:
        scheduler.sort(key=lambda x: x[0])
        
        current_event_time, event_type = scheduler.pop(0)
        
        if event_type == 1:
            arrival(current_event_time)
        elif event_type == 0:
            departure(current_event_time)

    print_result()

if __name__ == "__main__":
    main()