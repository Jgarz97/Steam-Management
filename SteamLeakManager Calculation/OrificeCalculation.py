from fluids.flow_meter import differential_pressure_meter_solver
from VaporProperties import Vapor_Properties  # Ensure this matches the filename of your VaporProperties class
from dataclasses import dataclass

# Constants
fuel_cc = 0.85  # Example carbon content of the fuel (kg C per kg of fuel)
fuel_mw = 16.04  # Example molecular weight of the fuel (kg/kg-mole)
mvc = 849.5 #scf/kg mole (molar volume conversion factor)
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

    temp_F: float
    press_PSIA: float
    superheat: bool
    enthalpy_BTUlbs: float
    entropy_BTUlbsR: float
    rate: float  # Steam leak rate in PPH
    fuel_cost: float  # Fuel cost of the steam leak in $/year
    water_cost: float  # Water cost of the steam leak in $/year
    accumulated_cost: float  # Accumulated cost of the steam leak in $/year
    gas_waste: float  # Fuel gas waste in ft3/year
    CO2_emissions: float  # Annual CO2 emissions in tons/year

    def __str__(self):
        report = {
            "Steam Temperature (F)": self.temp_F,
            "Steam Pressure (PSIA)": self.press_PSIA,
            "Superheated": "Yes" if self.superheat else "No",
            "Enthalpy (BTU/lb)": f"{self.enthalpy_BTUlbs:.4f}",
            "Entropy (BTU/lb·R)": f"{self.entropy_BTUlbsR:.4f}",
            "Steam Leak Rate (PPH)": f"{self.rate:,.4f}",
            "Fuel Gas Waste (ft3/year)": f"{self.gas_waste:,.4f}",
            "Fuel Cost ($/year)": f"${self.fuel_cost:,.2f}",
            "Water Cost ($/year)": f"${self.water_cost:,.2f}",
            "Accumulated Cost ($/year)": f"${self.accumulated_cost:,.2f}",
            "CO2 Emissions (tons/year)": f"{self.CO2_emissions:,.4f}"
        }
        
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
        self.pipe_diameter = pipe_diameter * 0.0254  # Convert diameter to meters
        self.orifice_diameter = orifice_diameter * 0.0254  # Convert diameter to meters
        self.upstream_pressure = upstream_pressure * 6894.75729  # Convert pressure to Pa
        self.downstream_pressure = downstream_pressure * 6894.75729  # Convert pressure to Pa
        

        self.rho = self.vapor_properties.calculate_density() * 16.0185  # Convert density to kg/m^3
        self.mu = self.vapor_properties.calculate_viscosity() * 1.48816e-5  # Convert viscosity to Pa.s
    
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
        
        # Calculate enthalpy and entropy
        enthalpy = self.vapor_properties.calculate_enthalpy()
        entropy = self.vapor_properties.calculate_entropy()
        
        # Calculate costs and wastes
        steam_fuel_waste = ((mass_flow_rate_pph3 / 1000) * 8760 * enthalpy * Fuel_Cost) / Boiler_Efficiency
        steam_water_waste = Water_Cost * mass_flow_rate_pph3 * 8760
        steam_accumulated_cost = steam_fuel_waste + steam_water_waste
        fuel_gas_waste = (((((enthalpy - BFW_Enthalpy) * (mass_flow_rate_pph3 * (10 ** 3)))/(Boiler_Efficiency))/(Net_HV)))
        annual_CO2_emissions = (44/12) * fuel_gas_waste * fuel_cc * mvc * 0.001

        return SteamLeakReport(
            temp_F=self.vapor_properties.temperature_F,
            press_PSIA=self.vapor_properties.pressure_PSIA,
            superheat=self.vapor_properties.superheated,
            enthalpy_BTUlbs=enthalpy,
            entropy_BTUlbsR=entropy,
            rate=mass_flow_rate_pph,
            fuel_cost=steam_fuel_waste,
            water_cost=steam_water_waste,
            accumulated_cost=steam_accumulated_cost,
            gas_waste=fuel_gas_waste,
            CO2_emissions=annual_CO2_emissions
        )