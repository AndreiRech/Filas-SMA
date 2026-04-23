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
