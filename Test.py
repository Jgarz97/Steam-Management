import numpy as np
from CoolProp.CoolProp import PropsSI
import fluids

def orifice_flow_rate(diameter_in, pressure_upstream_psi, pressure_downstream_psi, temperature_F, discharge_coefficient=0.6):
    # Convert units
    diameter_m = diameter_in * 0.0254  # inches to meters
    pressure_upstream_pa = pressure_upstream_psi * 6894.76  # psi to Pascals
    pressure_downstream_pa = pressure_downstream_psi * 6894.76  # psi to Pascals
    temperature_K = (temperature_F + 459.67) * 5/9  # Fahrenheit to Kelvin

    # Calculate the area of the orifice
    area_m2 = np.pi * (diameter_m / 2)**2

    # Get the density of steam at the upstream conditions using CoolProp
    density_upstream = PropsSI('D', 'T', temperature_K, 'P', pressure_upstream_pa, 'IF97::Water')
    
    # Calculate the pressure drop
    delta_p = pressure_upstream_pa - pressure_downstream_pa

    # Calculate the mass flow rate using the orifice equation from fluids library
    mass_flow_rate = fluids.flow_meter.orifice_(pressure_upstream_pa, pressure_downstream_pa, diameter_m, diameter_m, discharge_coefficient, density_upstream, density_upstream)
    
    return mass_flow_rate

# Example usage
diameter_in = 0.5  # 10 mm orifice diameter
pressure_upstream_psi = 2614.7  # 290 psi upstream pressure
pressure_downstream_psi = 14.7  # 1 atm downstream pressure
temperature_F = 640  # 500 °F upstream temperature

mass_flow_rate = orifice_flow_rate(diameter_in, pressure_upstream_psi, pressure_downstream_psi, temperature_F)
print(f"Mass flow rate through the orifice: {mass_flow_rate:.4f} kg/s")
