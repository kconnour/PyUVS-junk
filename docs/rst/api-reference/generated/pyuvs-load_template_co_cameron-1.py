import matplotlib.pyplot as plt
import pyuvs as pu

fig, ax = plt.subplots()

template = pu.load_template_co_cameron()
wavelengths = pu.load_template_wavelengths()
ax.plot(wavelengths, template)
ax.set_xlim(wavelengths[0], wavelengths[-1])
ax.set_xlabel('Wavelength [nm]')
ax.set_ylabel('Relative brightness')

plt.show()