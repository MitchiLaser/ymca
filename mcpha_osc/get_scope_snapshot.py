#!/usr/bin/env python3

import osc
import numpy as np
import matplotlib.pyplot as plt

Osc = osc.Osc("10.42.0.107")
data = Osc.get_data()

x = np.arange(Osc.tot)
plt.plot(x, data[0::2], label="Chanel 1")
plt.plot(x, data[1::2], label="Chanel 2")
plt.show()
