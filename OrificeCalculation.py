from fluids.flow_meter import differential_pressure_meter_solver
from VaporProperties import Vapor_Properties  # Ensure this matches the filename of your VaporProperties class
from dataclasses import dataclass



Fuel_Cost = 6.0  # Cost of fuel in $/MMBTU
Water_Cost = 1.17  # Cost of water in $/lb
Boiler_Efficiency = 0.8  # Efficiency of the boiler
BFW_Enthalpy = 38.1179  # Enthalpy of the boiler feed water in BTU/lb
Net_HV = 900  # Net heating value of the fuel in BTU/ft3

@dataclass
class SteamLeakReport:
    '''
    class that contains information pertaining to a steam leak such as the steam leak rate, fuel cost of the steam leak, 
        water cost of the steam leak, accumulated cost of the steam leak, and fuel gas waste
    '''

    rate: float # Steam leak rate in PPHq
    fuel_cost: float # Fuel cost of the steam leak in $/year
    water_cost: float # Water cost of the steam leak in $/year
    accumulated_cost: float # Accumulated cost of the steam leak in $/year
    gas_waste: float # Fuel gas waste in ft3/year

    def __str__(self):
        report = {"Steam leak rate": self.rate,
                  "Fuel Cost": self.fuel_cost, 
                  "Water Cost": self.water_cost, 
                  "Accumulated Cost": self.accumulated_cost, 
                  "Fuel Gas Waste": self.gas_waste}
        
        s = ""
        for key, value in report.items():
            s += f"{key}: {value}\n"
        s = s.strip()
        
        return s

class SteamLeakCalculator:
    '''
    Class to calculate the steam leak rate through an orifice
    '''

    k = 1.3  # Isentropic exponent for steam
    taps = 'D/2'  # Tap orientation
    meter_type = 'ISO 5167 orifice'  # Specify the meter type (ISO 5167 orifice)

    def __init__(self, vapor_properties, pipe_diameter, orifice_diameter, upstream_pressure, downstream_pressure):
        '''
        vapor_propetries: Vapor_Properties object, i.e., temperature, pressure, and quality
        pipe_diameter_inches: float, pipe diameter (in meters)
        orifice_diameter: float, orifice diameter (in meters)
        upstream_pressure: float, upstream pressure (in psi)
        downstream_pressure: float, downstream pressure (in psi)
        convert_units: tuple (str, str), units to convert the input values from 
        '''
        self.vapor_properties = vapor_properties
        self.pipe_diameter = pipe_diameter
        self.orifice_diameter = orifice_diameter
        self.upstream_pressure = upstream_pressure
        self.downstream_pressure = downstream_pressure
        

        self.rho = self.vapor_properties.calculate_vapor_density() * 16.0185  # Convert density to kg/m^3
        self.mu = self.vapor_properties.calculate_vapor_viscosity() * 1.48816e-5  # Convert viscosity to Pa.s
    
    def calculate_steam_leak(self):
        '''
        Calculate the steam leak rate through the orifice

        Returns:
        SteamLeakReport object
        '''

        # Calculate the mass flow rate using the differential pressure meter solver
        mass_flow_rate_kg_s = differential_pressure_meter_solver(
            D=self.pipe_diameter,
            rho=self.rho,
            mu=self.mu,
            k=self.k,
            D2=self.orifice_diameter,
            P1=self.upstream_pressure,
            P2=self.downstream_pressure,
            meter_type=self.meter_type,
            taps=self.taps
        )

        # Convert the mass flow rate to PPH
        mass_flow_rate_pph = mass_flow_rate_kg_s * 7936.64
        mass_flow_rate_pph3 = mass_flow_rate_pph * 10 ** -3
        steam_fuel_waste = ((mass_flow_rate_pph3 / 1000) * 8760 * self.vapor_properties.calculate_enthalpy() * Fuel_Cost) / Boiler_Efficiency
        steam_water_waste = Water_Cost * mass_flow_rate_pph3 * 8760
        steam_accumulated_cost = steam_fuel_waste + steam_water_waste
        fuel_gas_waste = (((((self.vapor_properties.calculate_enthalpy() - BFW_Enthalpy) * (mass_flow_rate_pph3 * (10 ** 3)))/(Boiler_Efficiency))/(Net_HV)))


        return SteamLeakReport(rate=mass_flow_rate_pph, fuel_cost=steam_fuel_waste, water_cost=steam_water_waste, accumulated_cost=steam_accumulated_cost, gas_waste=fuel_gas_waste)