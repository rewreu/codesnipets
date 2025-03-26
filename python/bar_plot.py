import numpy as np
import matplotlib.pyplot as plt

x = np.arange(len(result['A']))  # label locations
width = 0.25  # width of the bars

plt.figure(figsize=(10, 6))
plt.bar(x - width, result['B'], width, label='B mean')
plt.bar(x,         result['C'], width, label='C mean')
plt.bar(x + width, result['D'], width, label='D mean')

plt.xticks(x, result['A'], rotation=45)
plt.xlabel('A')
plt.ylabel('Mean Values')
plt.title('Mean of B, C, D grouped by A')
plt.legend()
plt.tight_layout()
plt.show()
