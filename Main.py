from OrificeCalculation import SteamLeakCalculator
from VaporProperties import Vapor_Properties  # Ensure this matches the filename of your VaporProperties class

# Example parameters to pass to the function
temperature_F = 640  # Example temperature in Fahrenheit for superheated steam
pressure_PSIA = 600  # Example pressure in psia
D_inches = 100
D2_inches = 1
P1_psi = 600
P2_psi = 0

# Create an instance of VaporProperties
vapor_props = Vapor_Properties(temperature_F, pressure_PSIA, superheated=True)
#vapor_props.print_properties()

# Create an instance of SteamLeakCalculator
calculator = SteamLeakCalculator(vapor_props, D_inches, D2_inches, P1_psi, P2_psi)

# Call the calculate_steam_leak method and print all results
results = calculator.calculate_steam_leak()


print("Calculation Results:")
for key, value in results.items():
    if key in ["steam_fuel_cost", "steam_water_cost", "steam_accumulated_cost"]:
        print(f"{key}: ${value:,.2f}")
    elif isinstance(value, float):
        print(f"{key}: {value:,.4f}")
    else:
        print(f"{key}: {value}")

# Print the mass flow rate in PPH from the results dictionary
print(f"Mass flow rate (PPH): {results['mass_flow_rate_pph']:,.4f} PPH")
