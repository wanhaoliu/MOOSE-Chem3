import math
import random
import numpy as np
import matplotlib.pyplot as plt

class GaussianModifier:
    def __init__(self, param):
        self.param = param
        self.extrema_pos = []
        self.special_pos = []
        self.max_amplitude = 0
        self.extrema_signs = []  # Store signs for extrema (+1 for max, -1 for min)
        self.special_types = []  # Store types for special points ("saddle" or "cliff")
        self._set_parameters()
        self._generate_positions()
        self.expression = ""  # Store the function expression
        self.num_maxima = 0
        self.num_minima = 0
        self.num_cliffs = 0
        self.num_saddles = 0
        self._count_features()

    def _set_parameters(self):
        if self.param == 1:
            self.num_extrema = random.randint(0, 6)
            # self.max_amplitude = 0.05
            self.num_special = random.randint(0, 1)
        elif self.param == 2:
            self.num_extrema = random.randint(6, 12)
            # self.max_amplitude = 0.35
            self.num_special = random.randint(1, 3)
        elif self.param == 3:
            self.num_extrema = random.randint(12, 60)
            # self.max_amplitude = 0.75
            self.num_special = random.randint(3, 6)
        else:
            raise ValueError("Parameter must be 1, 2, or 3")

    def _generate_positions(self):
        self.extrema_pos = [random.uniform(-100, -1) for _ in range(self.num_extrema)]
        self.special_pos = [random.uniform(-100, -1) for _ in range(self.num_special)]
        self.extrema_signs = [random.choice([1, -1]) for _ in range(self.num_extrema)]
        self.special_types = [random.choice(["saddle", "cliff"]) for _ in range(self.num_special)]

    def _count_features(self):
        self.num_maxima = sum(1 for sign in self.extrema_signs if sign == 1)
        self.num_minima = sum(1 for sign in self.extrema_signs if sign == -1)
        self.num_cliffs = sum(1 for s_type in self.special_types if s_type == "cliff")
        self.num_saddles = sum(1 for s_type in self.special_types if s_type == "saddle")

    def original_func(self, x):
        return math.exp(-(x**2) / 2000)

    def modified_func(self, x):
        y = self.original_func(x)
        
        # Scale factor to ensure perturbations don't push y too high
        scale_factor = 0.1  # Reduce perturbation impact
        
        for i, pos in enumerate(self.extrema_pos):
            sign = self.extrema_signs[i]
            amp = scale_factor  # Adjusted to keep y < 1
            y += sign * amp * math.exp(-((x - pos)**2) / 50)
        
        for i, pos in enumerate(self.special_pos):
            if self.special_types[i] == "saddle":
                scale = scale_factor * 0.1 * self.original_func(pos)
                y += scale * ((x - pos)**3 / 1000)
            else:  # cliff
                scale = scale_factor * 0.2 * self.original_func(pos)
                y += scale * math.tanh(10 * (x - pos))
        
        if abs(x) < 1e-6:
            return 1.0
        
        # Strictly enforce y < 1 for x != 0
        if abs(x) < 10:
            y = min(y, self.original_func(x))
            return max(y, 0.01)
        y = min(y, 0.98)
        return max(y, 0.01)

    def get_expression(self):
        # Build computer-readable expression
        expr = ["math.exp(-(x**2) / 2000)"]
        
        scale_factor = 0.1  # Match modified_func
        for i, (pos, sign) in enumerate(zip(self.extrema_pos, self.extrema_signs)):
            sign_str = "+" if sign == 1 else "-"
            term = f"{sign_str} {scale_factor:.4f} * math.exp(-((x - {pos:.2f})**2) / 50)"
            expr.append(term)
        
        for i, (pos, s_type) in enumerate(zip(self.special_pos, self.special_types)):
            if s_type == "saddle":
                scale = scale_factor * 0.1 * self.original_func(pos)
                term = f"+ {scale:.4f} * ((x - {pos:.2f})**3) / 1000"
            else:  # cliff
                scale = scale_factor * 0.2 * self.original_func(pos)
                term = f"+ {scale:.4f} * math.tanh(10 * (x - {pos:.2f}))"
            expr.append(term)
        
        main_expr = " ".join(expr)
        full_expr = (
            f"lambda x: 1.0 if abs(x) < 1e-6 else max(min({main_expr}, 0.98), 0.01)"
        )
        self.expression = full_expr
        
        # Human-readable description
        description = (
            f"The generated function contains:\n"
            f"- {self.num_maxima} maxima\n"
            f"- {self.num_minima} minima\n"
            f"- {self.num_cliffs} cliffs\n"
            f"- {self.num_saddles} saddles (platforms)"
        )
        return description, full_expr

# Example usage and plotting
param = 3
modifier = GaussianModifier(param)

# Print the function description and expression
description, expression = modifier.get_expression()
print(description)
print("\nFunction Expression:")
print(expression)

x = np.linspace(-100, 0, 1000)
y = [modifier.modified_func(xi) for xi in x]

plt.figure(figsize=(10, 6))
plt.plot(x, y, label="Modified Function")
plt.plot(x, [modifier.original_func(xi) for xi in x], '--', label="Original Function")
plt.scatter([0], [1], color='red', label="Fixed Point (0,1)")
plt.title(f"Modified Gaussian with Parameter {param}")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)
plt.legend()
plt.savefig("00000modified_gaussian.png")