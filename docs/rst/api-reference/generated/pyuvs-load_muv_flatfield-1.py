import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots(1, 1, figsize=(8, 2), constrained_layout=True)

flatfield = pu.load_muv_flatfield()
ax.pcolormesh(flatfield.T, vmin=0.9, vmax=1.1)
ax.set_xlabel('Spatial bin')
ax.set_ylabel('Spectral bin')

plt.show()