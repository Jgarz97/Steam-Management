from CoolProp.CoolProp import PropsSI
from dataclasses import dataclass

@dataclass
class VaporPropertiesReport:
    temp_F: float
    press_PSIA: float
    phase: str  # "vapor" or "liquid"
    superheat: bool = False  # Relevant only for vapor phase

    def __str__(self):
        report = {
            "Temperature": self.temp_F,
            "Pressure": self.press_PSIA,
            "Phase": self.phase,
            "Superheated": "Yes" if self.superheat else "No" if self.phase == "vapor" else "N/A"
        }
        s = ""
        for key, value in report.items():
            s += f"{key}: {value}\n"
        s = s.strip()
        
        return s

class Vapor_Properties:
    def __init__(self, temperature_F, pressure_PSIA, phase="vapor", superheated=False):
        self.temperature_F = temperature_F
        self.temperature_K = None
        self.pressure_PSIA = pressure_PSIA
        self.pressure_Pa = None
        self.phase = phase.lower()  # "vapor" or "liquid"
        self.superheated = superheated if self.phase == "vapor" else False
        self.saturation_temperature_F = None
        self.density_lbft3 = None
        self.enthalpy_BTUlbs = None
        self.entropy_BTUlbsR = None
        self.viscosity_lbfts = None
        self.cp_BTUlbsF = None
        self.cv_BTUlbsF = None

        if self.phase == "vapor" and not self.superheated:
            self.calculate_saturation_temperature()
    
    def _convert_temperature_to_K(self):
        """Convert temperature from Fahrenheit to Kelvin."""
        if self.temperature_K is None:
            self.temperature_K = (self.temperature_F + 459.67) * 5 / 9
        return self.temperature_K
    
    def _convert_pressure_to_Pa(self):
        """Convert pressure from PSIA to Pascals."""
        if self.pressure_Pa is None:
            self.pressure_Pa = self.pressure_PSIA * 6894.76
        return self.pressure_Pa

    def calculate_saturation_temperature(self):
        """Calculate the saturation temperature in Fahrenheit (vapor only)."""
        if self.pressure_Pa is None:
            self._convert_pressure_to_Pa()
        
        saturation_temperature_K = PropsSI('T', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        self.saturation_temperature_F = saturation_temperature_K * 9 / 5 - 459.67
        self.temperature_F = self.saturation_temperature_F  # Set temperature to saturation temperature
        self.temperature_K = saturation_temperature_K
        return self.saturation_temperature_F
    
    def calculate_density(self):
        """Calculate the density in lb/ft³."""
        if self.temperature_K is None:
            self._convert_temperature_to_K()
        if self.pressure_Pa is None:
            self._convert_pressure_to_Pa()
        
        if self.phase == "vapor" and self.superheated:
            density_kgm3 = PropsSI('D', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        elif self.phase == "vapor":
            density_kgm3 = PropsSI('D', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        elif self.phase == "liquid":
            density_kgm3 = PropsSI('D', 'P', self.pressure_Pa, 'Q', 0, 'IF97::Water')
        
        self.density_lbft3 = density_kgm3 * 0.06242796
        return self.density_lbft3
    
    def calculate_enthalpy(self):
        """Calculate the enthalpy in BTU/lb."""
        if self.temperature_K is None:
            self._convert_temperature_to_K()
        if self.pressure_Pa is None:
            self._convert_pressure_to_Pa()
        
        if self.phase == "vapor" and self.superheated:
            enthalpy_Jkg = PropsSI('H', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        elif self.phase == "vapor":
            enthalpy_Jkg = PropsSI('H', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        elif self.phase == "liquid":
            enthalpy_Jkg = PropsSI('H', 'P', self.pressure_Pa, 'Q', 0, 'IF97::Water')
        
        self.enthalpy_BTUlbs = enthalpy_Jkg * 0.000429922613
        return self.enthalpy_BTUlbs
    
    def calculate_entropy(self):
        """Calculate the entropy in BTU/lb·R."""
        if self.temperature_K is None:
            self._convert_temperature_to_K()
        if self.pressure_Pa is None:
            self._convert_pressure_to_Pa()

        if self.phase == "vapor" and self.superheated:
            entropy_JkgK = PropsSI('S', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        elif self.phase == "vapor":
            entropy_JkgK = PropsSI('S', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        elif self.phase == "liquid":
            entropy_JkgK = PropsSI('S', 'P', self.pressure_Pa, 'Q', 0, 'IF97::Water')
        
        self.entropy_BTUlbsR = entropy_JkgK * 0.000238845896627
        return self.entropy_BTUlbsR
    
    def calculate_viscosity(self):
        """Calculate the viscosity in lb/ft·s."""
        if self.temperature_K is None:
            self._convert_temperature_to_K()
        if self.pressure_Pa is None:
            self._convert_pressure_to_Pa()
        
        if self.phase == "vapor" and self.superheated:
            viscosity_Pas = PropsSI('V', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        elif self.phase == "vapor":
            viscosity_Pas = PropsSI('V', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        elif self.phase == "liquid":
            viscosity_Pas = PropsSI('V', 'P', self.pressure_Pa, 'Q', 0, 'IF97::Water')
        
        self.viscosity_lbfts = viscosity_Pas * 0.020885434273
        return self.viscosity_lbfts

    def calculate_cp(self):
        """Calculate the specific heat capacity at constant pressure in BTU/lb·F."""
        if self.temperature_K is None:
            self._convert_temperature_to_K()
        if self.pressure_Pa is None:
            self._convert_pressure_to_Pa()
        
        if self.phase == "vapor" and self.superheated:
            cp_JkgK = PropsSI('C', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        elif self.phase == "vapor":
            cp_JkgK = PropsSI('C', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        elif self.phase == "liquid":
            cp_JkgK = PropsSI('C', 'P', self.pressure_Pa, 'Q', 0, 'IF97::Water')
        
        self.cp_BTUlbsF = cp_JkgK * 0.000238845896627
        return self.cp_BTUlbsF
    
    def calculate_cv(self):
        """Calculate the specific heat capacity at constant volume in BTU/lb·F."""
        if self.temperature_K is None:
            self._convert_temperature_to_K()
        if self.pressure_Pa is None:
            self._convert_pressure_to_Pa()
        
        if self.phase == "vapor" and self.superheated:
            cv_JkgK = PropsSI('O', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        elif self.phase == "vapor":
            cv_JkgK = PropsSI('O', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        elif self.phase == "liquid":
            cv_JkgK = PropsSI('O', 'P', self.pressure_Pa, 'Q', 0, 'IF97::Water')
        
        self.cv_BTUlbsF = cv_JkgK * 0.000238845896627
        return self.cv_BTUlbsF



