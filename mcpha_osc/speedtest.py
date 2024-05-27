#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import osc
import sys
from tqdm import tqdm

osc = osc.Osc(sys.argv[1])


for i in tqdm(range(100)):
    data = osc.get_data()

print(f"Number of samples: {len(data)}")
# plot last sample to make sure it
x = np.arange(osc.tot)
plt.plot(x, data[0::2], label='Channel 1')
plt.plot(x, data[1::2], label='Channel 2')
plt.show()
