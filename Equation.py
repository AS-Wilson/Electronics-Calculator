from numpy import *
from sympy import *
from Variable import *
from UliEngineering.EngineerIO import *
import re


class Equation:
    """Common base class for equations, which have variables featuring tolerance(s)"""

    def __init__(self, expression, *variables, UoM="Unit(s)"):
        """equation must be handed in using the class referencer"""

        if not isinstance(expression, Expr):
            raise TypeError("Expression given must be a sympy expression object")

        else:
            self.expression = expression

        for variable in variables:
            if not isinstance(variable, Variable):
                raise TypeError("The variables to be used must be of an instance of the Variable class")

            else:
                try:
                    self.variables.append(variable)

                except AttributeError:
                    self.variables = [variable]

        self.values_list = self.calculate_values(self.expression, *self.variables)
        # Run the recursive calculate values function to get all possible equation values.

        self.UoM = UoM

        self.nominal = None
        self.tol_value = None
        self.tol_decimal = None
        self.tol_values_unique = None
        self.tol_decimals_unique = None

        self.tol_value_set = False
        self.tol_values_unique_set = False
        self.find_nominal()

        try:
            self.values_list.sort(key=lambda x: x[1])

            self.min_max_results = [self.values_list[0], self.values_list[-1]]
            self.minimum = self.values_list[0]
            self.maximum = self.values_list[-1]
            self.equation_tolerances()

        except TypeError:
            self.min_max_results = None
            self.minimum = None
            self.maximum = None

        self.pretty_print()

    ####################
    def pretty_print(self):
        """Method"""
        try:
            print("For the Equation ->", self.expression, "with the substitution variables ->", self.variables,
                  "- the following minima/maxima are found:")

            print("The nominal value of approximately ->",
                  format_value(float(self.nominal[1]), unit=self.UoM, significant_digits=6),
                  "is achieved when the variable parameters are ->", self.nominal[0])

            print("The minimum value of approximately ->",
                  format_value(float(self.minimum[1]), unit=self.UoM, significant_digits=6),
                  "is achieved when the variable parameters are ->", self.minimum[0])

            print("The maximum value of approximately ->",
                  format_value(float(self.maximum[1]), unit=self.UoM, significant_digits=6),
                  "is achieved when the variable parameters are ->", self.maximum[0])

            if self.tol_values_unique_set:
                print("The equations output tolerance values are then approximately plus/minus", self.tol_values_unique,
                      "which are decimal tolerances of approximately", self.tol_decimals_unique, "%\n")

            elif self.tol_value_set:
                print("The equations output tolerance value is then approximately plus/minus",
                      format_value(float(self.tol_value), unit=self.UoM, significant_digits=6),
                      "which is a decimal tolerance of approximately", round(self.tol_decimal*100), "%\n")

        except ValueError:
            print("The necessary number of variables have likely not yet been given to obtain numerical results for the"
                  " expression", self.expression, "\nAn example expression from the currently given substitute "
                                                  "variables is", self.values_list[0])

    ####################
    def find_nominal(self):
        """Method which uses regular expressions to search through the values list and find the nominal value,
        this is assumed to be when all values of the equation are nominal."""
        minimal_pattern = re.compile(r"^((?!minimal).)*$", re.IGNORECASE | re.MULTILINE)
        maximal_pattern = re.compile(r"^((?!maximal).)*$", re.IGNORECASE | re.MULTILINE)
        check = 0

        for value in self.values_list:
            if re.findall(minimal_pattern, value[0]) and re.findall(maximal_pattern, value[0]):
                self.nominal = value
                check += 1

        if check != 1:
            raise ValueError("Something went wrong when setting the nominal value of equation")

    ####################
    def equation_tolerances(self):
        try:
            tol_minus = abs(self.minimum[1] - self.nominal[1])
            tol_plus = abs(self.nominal[1] - self.minimum[1])

            tol_dec_minus = tol_minus / self.nominal[1]
            tol_dec_plus = tol_plus / self.nominal[1]

        except TypeError:
            return

        if tol_minus == tol_plus:
            self.tol_value = tol_minus
            self.tol_decimal = tol_dec_minus
            self.tol_value_set = True

        else:
            self.tol_values_unique = [tol_plus, tol_minus]
            self.tol_decimals_unique = [tol_dec_plus, tol_dec_minus]
            self.tol_values_unique_set = True

    ####################
    def add_variable(self):
        """Method"""
        return 1

    ####################
    def update_values(self):
        """Method"""
        return 1

    ####################
    def __make_params(self, variable_name, current_parameter, existing_parameters=None):
        """Method for constructing the parameters of the current substitution upon an expression.
        Currently existing parameters from a previous substitution can be passed through as an argument to make a
        new string from it and the imminent substitution, or the parameters can be constructed purely from the
        imminent substitution if no additional arguments are passed in."""

        if existing_parameters is None:
            # No previous substitutions have been made so just make the current parameter str
            parameters = "%s %s" % (variable_name, current_parameter)
            return parameters

        else:
            # Substituting into an already substituted expression so the previous substitution parameter string must be
            #   appended to the next substituted parameter string
            if not isinstance(existing_parameters, str):  # Check if the previous params was definitely a string
                raise TypeError("Existing parameters being passed in must be a string")

            else:
                parameters = "%s %s, %s" % (variable_name, current_parameter, existing_parameters)
                return parameters

    ####################
    def __do_substitutions(self, expression, variable, existing_parameters=None):
        """Method to substitute the value(s) of an instance of the Variable class into a given expression.
        This method will return an array(s) with parameters followed by the resulting substitution, in the format:
        [parameter, substitution value/string]"""

        # Check the type of the passed in variable and assign the possible values and their order accordingly
        if variable.tol_type == 0:  # Both positive and negative tolerance
            parameter = ['Maximal', 'Nominal', 'Minimal']

        elif variable.tol_type == 1:  # ONLY positive tolerance
            parameter = ['Maximal', 'Nominal']

        elif variable.tol_type == 2:  # ONLY negative tolerance
            parameter = ['Nominal', 'Minimal']

        arr = None  # Initialise the list of values returned

        ##### ARGUMENTS VERIFICATION #####
        if existing_parameters is not None:
            if not isinstance(existing_parameters, str):
                raise TypeError("Existing parameters being passed in must be a string")

        ##### FUNCTION CONTENT #####
        if variable.nom_value and not (variable.tol_value_set or variable.tol_values_unique_set):
            # In this case, there is only a nominal value and no tolerances to consider.

            parameters = self.__make_params(variable, parameter[1], existing_parameters=existing_parameters)
            # Create the parameter string using make_params (eg. "x nom, y min...")

            substitute = expression.subs([(variable, variable.nom_value)])
            # Substitute the variables nominal value into the expression

            # Check if results array is None, make a list if so, otherwise append a the next list of parameters and
            #   values.
            if arr is None:
                arr = [[parameters, substitute]]

            else:
                arr.append([parameters, substitute])

            return arr

        elif (variable.tol_value_set or variable.tol_values_unique_set) and variable.nom_value:
            # There are tolerances so we will have to create a list/array in the form [parameters, expression/value]
            #   then add that to the existing values calculated or make a new list/array

            i = 0  # Attribute to track what new parameter we are currently substituting with

            for value in variable.value_range:

                parameters = self.__make_params(variable, parameter[i], existing_parameters=existing_parameters)
                # Create a string of the current parameters being substituted into the expression
                #   (eg. "x nom, y min...")

                substitute = expression.subs([(variable, value)])
                # Substitute the variables max, nom, min value into the expression

                if arr is None:  # Make array or add new values to the array
                    arr = [[parameters, substitute]]

                else:
                    arr.append([parameters, substitute])

                i += 1  # Increase index attribute by one for the next loop

            return arr  # The loop has finished and all substitutions are made so return the new list/array

    ####################
    def calculate_values(self, expr, *subs):
        """Method to recursively calculate the all possible values for the expression from the given instances of the
        Variable class. This will return a list of lists with each sub-list containing the parameters used to obtain the
        values, followed by the values themselves (in that order, i.e. [parameters, value resulting from parameters]).
        There may not be any numbers returned in the value field if not enough unknown variable values are given as
        arguments to the method."""

        ###### PSEUDOCODE #####
        ##### This is my best attempt at pseudocode this recursive functions operation
        #
        # def calculate_values(expr, vars):
        #   ## expr is the math expression we substitute values into.
        #   ##   vars is the list of Variable class instance arguments whose values will be substituted into the
        #   ##      expression.
        #
        #    if len(var) == 1:
        #    ##  This will be the base case, when there is only one variable passed into the function
        #
        #       return __do_substitutions(expr, var)
        #           ##  substitute the value of the variable into the expression and return the result
        #
        #
        #    else:
        #       ## There are still more variables to strip away so we need to recall the function after removing one
        #       ##  from the set of variable arguments currently passed into the function
        #
        #       recursive_call = calculate_values(expr, vars_with_one_less_var)  # Call func again with new parameters
        #
        #        for x in range(recursive_call)
        #            __do_substitutions(expr, var)
        #               ## Take the returned expression and substitute in the other (removed) variable then pass it back
        #               ##   to the function which called this instance
        ##### END OF PSEUDOCODE #####

        # This is the base case, substitutions will be made to the given expression with the values of Variable given.
        if len(subs) == 1:
            return self.__do_substitutions(expr, *subs)

        # Base case has not been met so we need to call the function again, with new (less) arguments
        else:
            substitutions = list(subs)
            # Argument tuples cannot be edited, so store the arguments for the next call of the function in a list

            return_array = None
            # Initialise the array of values to be returned later with None so that it will be initially assigned values
            #   correctly and later appended with new values correctly

            substitutions.pop(0)
            subbed_array = self.calculate_values(expr, *substitutions)
            # Remove the first value from the argument list the call this function again with these new values.
            #   The asterisk before 'substitutions' makes sure the arg list is unpacked before the function uses them.

            # Loop through the returned values substituting in the value that was removed when the function was
            #   re-called with the smaller parameter set above
            for params in subbed_array:
                if return_array is None:
                    return_array = self.__do_substitutions(params[1], subs[0], params[0])

                else:
                    return_array = return_array + (self.__do_substitutions(params[1], subs[0], params[0]))

            # Once all the values are substituted pass back the new list to whatever called the function
            return return_array

    ####################

