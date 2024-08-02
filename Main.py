from OrificeCalculation import SteamLeakCalculator
from VaporProperties import Vapor_Properties  # Ensure this matches the filename of your VaporProperties class
from dataclasses import dataclass

# Create an instance of VaporProperties
vapor_props = Vapor_Properties(temperature_F=640, pressure_PSIA=100, superheated=False)

# Create an instance of SteamLeakCalculator
calculator = SteamLeakCalculator(vapor_props, pipe_diameter=0.5, orifice_diameter=0.25, upstream_pressure=600, downstream_pressure=300)

# Fuel properties
fuel_cc = 0.85  # Example carbon content of the fuel (kg C per kg of fuel)
fuel_mw = 16.04  # Example molecular weight of the fuel (kg/kg-mole)


# Call the calculate_steam_leak method and print all results
results = calculator.calculate_steam_leak()
inputs = vapor_props.get_report()




print("Calculation Results:")
print(f"Steam Pressure: {inputs.press_PSIA} PSIA")
print(f"Steam Temperature: {inputs.temp_F} F")
print(f"Superheated: {'Yes' if inputs.superheat else 'No'}")
print(f"Steam Leak Rate: {results.rate:,.4f} PPH")
print(f"Fuel Cost: ${results.fuel_cost:,.2f}")
print(f"Water Cost: ${results.water_cost:,.2f}")
print(f"Accumulated Cost: ${results.accumulated_cost:,.2f}")
print(f"Fuel Gas Waste: {results.gas_waste:,.4f} ft3/year")


