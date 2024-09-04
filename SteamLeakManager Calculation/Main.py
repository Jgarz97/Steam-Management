
from OrificeCalculation import SteamLeakCalculator
from VaporProperties import Vapor_Properties
from dataclasses import dataclass

# Create an instance of VaporProperties for vapor (superheated steam)
vapor_props = Vapor_Properties(temperature_F=750, pressure_PSIA=614.7, phase="Vapor", superheated=True)

# Create an instance of SteamLeakCalculator
calculator = SteamLeakCalculator(vapor_props, pipe_diameter=100, orifice_diameter=1, upstream_pressure=600, downstream_pressure=14.7)

# Call the calculate_steam_leak method and print all results
results = calculator.calculate_steam_leak()

print("Vapor Properties Report:")
print(results)


