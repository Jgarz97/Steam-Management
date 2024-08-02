from CoolProp.CoolProp import PropsSI
from dataclasses import dataclass

@dataclass
class Vapor_Properties_Report:
    temp_F: float
    press_PSIA: float
    superheat: bool

    def __str__(self):
        report = {"Steam Temperature": self.temp_F,
                  "Steam Pressure": self.press_PSIA,
                  "Superheated": self.superheat}
        
        s = ""
        for key, value in report.items():
            s += f"{key}: {value}\n"
        s = s.strip()
        
        return s

class Vapor_Properties:
    def __init__(self, temperature_F, pressure_PSIA, superheated=False):
        self.temperature_F = temperature_F
        self.temperature_K = None
        self.pressure_PSIA = pressure_PSIA
        self.pressure_Pa = None
        self.superheated = superheated
        self.saturation_temperature_F = None
        self.vapor_density_lbft3 = None
        self.enthalpy_BTUlbs = None
        self.vapor_viscosity_lbfts = None
        self.cp_BTUlbsF = None
        self.cv_BTUlbsF = None
    
    def convert_temperature_K(self):
        if self.temperature_K is None:
            self.temperature_K = (self.temperature_F + 459.67) * 5/9
        return self.temperature_K
    
    def convert_pressure_Pa(self):
        if self.pressure_Pa is None:
            self.pressure_Pa = self.pressure_PSIA * 6894.76
        return self.pressure_Pa

    def calculate_saturation_temperature(self):
        if self.pressure_Pa is None:
            self.convert_pressure_Pa()
        
        saturation_temperature_K = PropsSI('T', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        self.saturation_temperature_F = saturation_temperature_K * 9/5 - 459.67
        return self.saturation_temperature_F
    
    def calculate_vapor_density(self):
        if self.temperature_K is None:
            self.convert_temperature_K()
        if self.pressure_Pa is None:
            self.convert_pressure_Pa()
        
        if self.superheated:
            density_kgm3 = PropsSI('D', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        else:
            density_kgm3 = PropsSI('D', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        
        self.vapor_density_lbft3 = density_kgm3 * 0.06242796
        return self.vapor_density_lbft3
    
    def calculate_enthalpy(self):
        if self.temperature_K is None:
            self.convert_temperature_K()
        if self.pressure_Pa is None:
            self.convert_pressure_Pa()
        
        if self.superheated:
            enthalpy_Jkg = PropsSI('H', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        else:
            enthalpy_Jkg = PropsSI('H', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        
        self.enthalpy_BTUlbs = enthalpy_Jkg * 0.000429922613
        return self.enthalpy_BTUlbs
    
    def calculate_vapor_viscosity(self):
        if self.temperature_K is None:
            self.convert_temperature_K()
        if self.pressure_Pa is None:
            self.convert_pressure_Pa()
        
        if self.superheated:
            viscosity_Pas = PropsSI('V', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        else:
            viscosity_Pas = PropsSI('V', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        
        self.vapor_viscosity_lbfts = viscosity_Pas * 0.020885434273
        return self.vapor_viscosity_lbfts
    
    def calculate_cp(self):
        if self.temperature_K is None:
            self.convert_temperature_K()
        if self.pressure_Pa is None:
            self.convert_pressure_Pa()
        
        if self.superheated:
            cp_JkgK = PropsSI('C', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        else:
            cp_JkgK = PropsSI('C', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        
        self.cp_BTUlbsF = cp_JkgK * 0.000238845896627
        return self.cp_BTUlbsF
    
    def calculate_cv(self):
        if self.temperature_K is None:
            self.convert_temperature_K()
        if self.pressure_Pa is None:
            self.convert_pressure_Pa()
        
        if self.superheated:
            cv_JkgK = PropsSI('O', 'T', self.temperature_K, 'P', self.pressure_Pa, 'IF97::Water')
        else:
            cv_JkgK = PropsSI('O', 'P', self.pressure_Pa, 'Q', 1, 'IF97::Water')
        
        self.cv_BTUlbsF = cv_JkgK * 0.000238845896627
        return self.cv_BTUlbsF
    

    def get_report(self):
        if not self.superheated:
            self.calculate_saturation_temperature()
            return Vapor_Properties_Report(
                temp_F=self.saturation_temperature_F,
                press_PSIA=self.pressure_PSIA,
                superheat=self.superheated
            )
        else:
            self.calculate_saturation_temperature()
            return Vapor_Properties_Report(
                temp_F=self.temperature_F,
                press_PSIA=self.pressure_PSIA,
                superheat=self.superheated
        )