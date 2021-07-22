# from UliEngineering.Electronics.Resistors import *
# from UliEngineering.EngineerIO import *
# # Includes functions involving E96 resistor values
#
# # Windows install above modules:
# # python -m pip install https://github.com/ulikoehler/UliEngineering/archive/refs/heads/master.zip
#
# # Linux install above modules:
# # sudo pip3 install git+https://github.com/ulikoehler/UliEngineering.git

from Variable import *
from Equation import *
from sympy import *

def main():
    ## Example based on LTC4418 IC datasheet - https://www.analog.com/en/products/ltc4418.html
    print("Calculations for the Hysteresis Pin Resistor to Ground, and OV/UV Pins current:")
    r_hys = Variable('R_hys', nom_value=Float(255000.0), tol_decimal=Float(0.01))
    i_ext = Float(0.063) / r_hys
    i_ext = Equation(i_ext, r_hys, UoM='Amps')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
