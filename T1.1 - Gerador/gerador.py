import matplotlib.pyplot as plt

# - Funções para o Exercício 1 (validar os números aleatórios criados)

def create_graph(idx: range, numbers: list[int]):
    plt.figure(figsize=(10, 6))
    plt.scatter(idx, numbers, alpha=0.6, edgecolors='b', s=10)
    plt.title('Gráfico de Dispersão Congruente Linear')
    plt.xlabel('Índice (1 a 1000)')
    plt.ylabel('Pseudoaleatório (0 a 1)')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.savefig("grafico_dispersao_mcl.png", dpi=300)

    plt.show()

def save_file(numbers: list[int]):
    with open("pseudoaleatorios_1000.txt", "w") as f:
        for num in numbers:
            f.write(f"{num:.6f}\n")

def randomize(amount: int, seed: int, a: int, c: int, M: int) -> list[int]:
    numbers = []
    xi = seed

    for _ in range(amount):
        x_next = (a * xi + c) % M
        U = x_next / M
        numbers.append(U)
        xi = x_next

    return numbers

def verify_random(numbers: list[int]) -> bool:
    set_num = set()
    for num in numbers:
        set_num.add(num)

    print(f"Total of unique numbers: {len(set_num)}")
    return len(set_num) == len(numbers)

def verify_params(a: int, c: int, M: int, X0: int, amount: int) -> bool:
    if M <= 0:
        print("'M' should be a positive number")
        return False

    if a <= 0 or a >= M:
        print("'a' should be positive and less then 'M'")
        return False

    if c < 0 or c >= M:
        print("'c' should be positive and less then 'M'")
        return False
    
    if X0 < 0 or X0 >= M:
        print("'X0' should be positive and less then 'M'")
        return False
    
    if M < amount:
        print("'M' should be a greater then the total of numbers")
        return False
    
    return True

def main():
    X0 = 9013      
    a = 709         
    c = 5678341     
    M = 2**23         
    amount = 1000

    if not verify_params(a, c, M, X0, amount):
        return
    
    numbers = randomize(amount, X0, a, c, M)

    if not verify_random(numbers):
        return
    
    save_file(numbers)

    idx = range(1, amount + 1)
    create_graph(idx, numbers)

main()