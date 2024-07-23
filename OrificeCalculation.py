from fluids.flow_meter import differential_pressure_meter_solver
from VaporProperties import Vapor_Properties  # Ensure this matches the filename of your VaporProperties class

Fuel_Cost = 6.0  # Cost of fuel in $/MMBTU
Water_Cost = 1.17  # Cost of water in $/lb
Boiler_Efficiency = 0.8  # Efficiency of the boiler
BFW_Enthalpy = 38.1179  # Enthalpy of the boiler feed water in BTU/lb
Net_HV = 900  # Net heating value of the fuel in BTU/ft3

class SteamLeakCalculator:
    def __init__(self, vapor_properties, D_inches, D2_inches, P1_psi, P2_psi):
        self.vapor_properties = vapor_properties
        self.D_inches = D_inches
        self.D2_inches = D2_inches
        self.P1_psi = P1_psi
        self.P2_psi = P2_psi
    
    def calculate_steam_leak(self):
        # Convert to metric units
        D = self.D_inches * 0.0254  # Convert pipe diameter to meters
        D2 = self.D2_inches * 0.0254  # Convert orifice diameter to meters
        rho = self.vapor_properties.calculate_vapor_density() * 16.0185  # Convert density to kg/m^3
        mu = self.vapor_properties.calculate_vapor_viscosity() * 1.48816e-5  # Convert viscosity to Pa.s
        P1 = self.P1_psi * 6894.76  # Convert upstream pressure to Pascals
        P2 = self.P2_psi * 6894.76  # Convert downstream pressure to Pascals
        k = 1.3  # Isentropic exponent for steam
        taps = 'D/2'  # Tap orientation

        # Specify the meter type (ISO 5167 orifice)
        meter_type = 'ISO 5167 orifice'

        # Calculate the mass flow rate using the differential pressure meter solver
        mass_flow_rate_kg_s = differential_pressure_meter_solver(
            D=D,
            rho=rho,
            mu=mu,
            k=k,
            D2=D2,
            P1=P1,
            P2=P2,
            meter_type=meter_type,
            taps=taps
        )

        # Convert the mass flow rate to PPH
        mass_flow_rate_pph = mass_flow_rate_kg_s * 7936.64
        mass_flow_rate_pph3 = mass_flow_rate_pph * 10 ** -3
        steam_fuel_waste = ((mass_flow_rate_pph3 / 1000) * 8760 * self.vapor_properties.calculate_enthalpy() * Fuel_Cost) / Boiler_Efficiency
        steam_water_waste = Water_Cost * mass_flow_rate_pph3 * 8760
        steam_accumulated_cost = steam_fuel_waste + steam_water_waste
        fuel_gas_waste = (((((self.vapor_properties.calculate_enthalpy() - BFW_Enthalpy) * (mass_flow_rate_pph3 * (10 ** 3)))/(Boiler_Efficiency))/(Net_HV)))

        return {
            "mass_flow_rate_pph": mass_flow_rate_pph,
            #"mass_flow_rate_kg_s": mass_flow_rate_kg_s,
            #"mass_flow_rate_pph3": mass_flow_rate_pph3,
            "steam_fuel_cost": steam_fuel_waste,
            "steam_water_cost": steam_water_waste,
            "steam_accumulated_cost": steam_accumulated_cost,
            "fuel_gas_waste": fuel_gas_waste,
            #"rho": rho,
            #"mu": mu,
            #"P1": P1,
            #"P2": P2,
            #"D": D,
            #"D2": D2,
        }
