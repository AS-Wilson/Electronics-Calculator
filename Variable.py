from numpy import *
from sympy import *


# Includes functions for defining an equation which has variables


class Variable(Symbol):
	"""Class which inherits from the SymPy "Symbol" class.

	This class provides attributes and methods to track, assign, and calculate, variable's nominal values, tolerances,
	and resulting possible value range resulting from these two properties."""

	def __init__(self, *args, nom_value=0.0, tol_pref=0, tol_type=0, unique_tolerances=False, tol_decimal=0.0,
				 tol_value=0.0, tol_decimals_unique=None, tol_values_unique=None):

		super(Variable, self)  # Initialise SymPy's "Symbol" base class

		self.nom_value = nom_value  # This is the nominal value of the variable

		self.tol_pref = tol_pref
		##### TOLERANCE PREFERENCE #####
		# What is the preferred tolerance value when nom_value is updated?
		# Default (0) is percent tolerance. 		1 indicates that a fixed tolerance value is preferred

		self.tol_type = tol_type
		##### TOLERANCE TYPE #####
		# Sets the type of tolerance range, (+ve/-ve, only +ve, only -ve)
		# Default value (0) is a plus or minus (+ve/-ve) type of tolerance.
		# 1 is purely positive (+ve) tolerance.		2 is purely negative (-ve) tolerance.

		self.unique_tolerances = unique_tolerances
		# Attribute to track if the plus tolerance value is different to the minus value tolerance (this is
		# fairly common in, for example, voltage tolerances at inputs, outputs, and internals of ICs.)

		if self.unique_tolerances:
			# Check if we have unique (different) plus/minus tolerance values, then assign either decimal or numeric
			# tolerance values depending on what the instance is initialised with.
			if tol_decimals_unique and tol_values_unique:
				raise ValueError(
					'There can be only one... tolerance definition (i.e. only define tol_decimal or tol_value')

			elif tol_decimals_unique:
				self.tol_decimals_unique = tol_decimals_unique

			elif tol_values_unique:
				self.tol_values_unique = tol_values_unique

		elif tol_decimal and tol_value:
			raise ValueError('There can be only one... tolerance definition (i.e. only define tol_decimal or tol_value')

		elif tol_decimal:
			self.tol_decimal = tol_decimal
			self._tol_values_unique_set = False
			# Tracking attribute to quickly check if the instance as unique tol's, same with other assignments in
			# the other branches below

		elif tol_value:
			self.tol_value = tol_value
			self._tol_values_unique_set = False

		else:
			self._tol_value_set = False  # Tracking attribute to quickly check if the instance has ordinary tolerances
			self._tol_values_unique_set = False

		self.update_value_range()

	def pretty_print(self):
		if self.nom_value_set and self.tol_value_set and self.tol_decimal != 0:
			return str(("Variable " + str(self.name) + " has a Nominal Value of " + str(self.nom_value) + " and a tolerance of " + str((self.tol_decimal * 100)) + "%"))
	# 	return "Nothing defined yet."

	#########################

	# Nominal value getter/setter, and a tracking property to see if it has been set
	@property
	def nom_value(self):
		"""Getter method for the variable class' nominal value, this returns the "private" _nom_value attribute"""
		return self._nom_value

	@nom_value.setter
	def nom_value(self, value=0.0):
		"""Setter method for the variable class' nominal value.

		Checks if a valid type is passed in, then sets the private variable _nom_value, after which it sets
		_nom_value_set (intended to allow quick checking of the instance's nominal value properties) depending on
		whether a non zero value was passed in."""
		if not isinstance(value, float) and not isinstance(value, Float):
			raise TypeError('The variables nominal value (nom_value) must be of type float.')

		else:
			self._nom_value = value

			if self.nom_value != 0:
				self._nom_value_set = True

			else:
				self._nom_value_set = False

	@property
	def nom_value_set(self):
		"""Getter method for the variable class' nominal value setting.

		True if there is a nominal Value, false if not."""
		return self._nom_value_set

	#########################

	@property
	def tol_pref(self):
		"""Getter method for the class' tolerance preference for either a decimal/percentage tolerance,
		or a numerical tolerance.

		This matters when you reassign the nominal value and need to recalculate value ranges"""
		return self._tol_pref

	@tol_pref.setter
	def tol_pref(self, value=0):
		"""Setter Method for the class' tolerance preference.

		This method ensures the correct data and value is passed in then, if valid, assigns the passed in preference
		value.
		Defaults to 0 = decimal tolerance preferred, the other option is 1 = numeric tolerance preferred."""
		if not isinstance(value, int):
			raise TypeError('The tolerance preference must be of type int')

		if not value >= 0 or not value <= 1:
			raise ValueError('The tolerance preference (tol_pref) only has valid values of 0 '
							 '(decimal tolerance preferred) or 1 (numeric tolerance preferred)')

		else:
			self._tol_pref = value

	#########################

	@property
	def tol_type(self):
		"""Getter method for the class' tolerance type.

		0 = Plus and Minus tolerance, 1 = Only Positive tolerance, and 2 = ONLY Negative tolerance."""
		return self._tol_type

	@tol_type.setter
	def tol_type(self, value=0):
		"""Setter Method for the class' tolerance type.

		Checks if the correct data type and a valid value has been
		passed in, then assigns to the private attribute if true."""
		if not isinstance(value, int):
			raise TypeError('The tolerance type must be of type int')

		if not value >= 0 or not value <= 2:
			raise ValueError('The tolerance type (tol_type) only has valid values of 0 (plus/minus value), '
							 '1 (only positive), and 2 (only negative)')

		elif value == 0:
			self._tol_type = value

		else:
			self._tol_type = value
			self._unique_tolerances = False

	#########################

	@property
	def tol_decimal(self):
		"""Getter method for class' decimal/percentage tolerance property"""
		return self._tol_decimal

	@tol_decimal.setter
	def tol_decimal(self, value=0.0):
		"""Setter method for class' decimal/percentage tolerance property.

		Checks if a float between 0 and 1 has been given, then calculates and assigns the numerical tolerance if
		 possible; this will also result in the _tolerance_value_set flag being set, and the _tol_pref property being
		 set if successful."""
		if not isinstance(value, float) and not isinstance(value, Float):
			raise TypeError('The variables tolerance value (tol_value) must be of type float.')

		elif self._unique_tolerances:
			raise ValueError(
				'As you have set the variable to have different plus / minus values (unique_tolerances '
				'evaluates as true you cannot use this attribute')

		elif value == 0:
			self.tol_pref = 0
			self._tol_decimal = value
			self._tol_value = 0.0
			self._tol_value_set = False
			self._unique_tolerances = False

		else:
			self.tol_pref = 0
			self._tol_decimal = value

			if self.nom_value:
				self._tol_value = self.nom_value * self._tol_decimal
				self._tol_value_set = True
				self._unique_tolerances = False

			else:
				self._tol_value = 0.0
				self._tol_value_set = False
				self._unique_tolerances = False

	#########################

	@property
	def tol_value(self):
		"""Getter method for the numerical tolerance value."""
		return self._tol_value

	@tol_value.setter
	def tol_value(self, value=0.0):
		"""Setter method for the numeric tolerance value.

		Checks if a float has been given, then calculates and assigns the decimal tolerance if possible;
		this will also result in the _tolerance_value_set flag being set, and the _tol_pref property being
		set if successful."""
		if not isinstance(value, float) and not isinstance(value, Float):
			raise TypeError('The variables tolerance value (tol_value) must be of type float.')

		elif self._unique_tolerances:
			raise ValueError(
				'As you have set the variable to have different plus / minus values (unique_tolerances '
				'evaluates as true you cannot use this attribute')

		elif value == 0:
			self.tol_pref = 1
			self._tol_value = value
			self._tol_decimal = 0.0
			self._tol_value_set = False
			self._tol_values_unique_set = False

		else:
			self.tol_pref = 1
			self._tol_value = value
			self._tol_value_set = True
			self._tol_values_unique_set = False

			if self._nom_value_set:
				self._tol_decimal = self.tol_value / self.nom_value

			else:
				self._tol_decimal = 0.0

	#########################

	@property
	def tol_value_set(self):
		return self._tol_value_set

	#########################

	# TODO: comments
	@property
	def unique_tolerances(self):
		return self._unique_tolerances

	@unique_tolerances.setter
	def unique_tolerances(self, value=False):
		"""Method"""
		if not isinstance(value, bool):
			raise TypeError('This attribute (unique_tolerances) must be a boolean value.')

		else:
			self._unique_tolerances = value
			if value is True:
				self._tol_type = 0
				self._tol_value_set = False

	#########################

	# TODO: comments
	@property
	def tol_decimals_unique(self):
		return self._tol_decimals_unique

	@tol_decimals_unique.setter
	def tol_decimals_unique(self, decimals=[0.0, 0.0]):

		if not isinstance(decimals, list):
			raise TypeError('The unique tolerances must be handed in as a list')

		# elif (decimals.shape != array_check.shape) or (decimals.ndim != array_check.ndim):
		# 	raise ValueError('The array must be one dimensional with only 2 columns')

		elif not isinstance(decimals[0], float) or not isinstance(decimals[1], float):
			raise TypeError('The arrays values must be floats')

		elif decimals[0] == 0 or decimals[1] == 0:
			raise ValueError("Decimal tolerance values must be non-zero")

		elif self.tol_type != 0:
			raise ValueError("Tolerance Type can only be 0 when using unique tolerances")

		elif self.tol_type == 0:
			self._tol_decimals_unique = decimals
			self._tol_pref = 0

			if self.nom_value_set:
				self._tol_values_unique = [(self.nom_value * self.tol_decimals_unique[0]),
												(self.nom_value * self.tol_decimals_unique[1])]

				self._tol_values_unique_set = True

			else:
				self._tol_values_unique_set = False

	#########################

	# TODO:
	#  Comments
	#  Make the unique setters work
	@property
	def tol_values_unique(self):
		return self._tol_values_unique

	@tol_values_unique.setter
	def tol_values_unique(self, values=[0.0, 0.0]):
		# array_check = array([0, 0])

		if not isinstance(values, list):
			raise TypeError('The unique tolerances must be handed in as an numpy matrix / array')

		# elif (values.shape != array_check.shape) or (values.ndim != array_check.ndim):
		# 	raise ValueError('The array must be one dimensional with only 2 columns')

		elif not isinstance(values[0], float) or not isinstance(values[1], float):
			raise TypeError('The arrays values must be floats')

		elif values[0] == 0 or values[1] == 0:
			raise ValueError("Numeric tolerance values must be non-zero")

		elif self.tol_type != 0:
			raise ValueError("Tolerance Type can only be 0 when using unique tolerances")

		elif self.tol_type == 0:
			self._tol_values_unique = values
			self._tol_values_unique_set = True
			self._tol_pref = 1

			if self.nom_value_set and self._tol_values_unique[0] != 0 and self._tol_values_unique[1] != 0:
				self._tol_decimals_unique = [(self.tol_values_unique[0] / self.nom_value),
												  (self.tol_values_unique[1] / self.nom_value)]

	@property
	def tol_values_unique_set(self):
		return self._tol_values_unique_set

	#########################

	# TODO: comments
	@property
	def value_range(self):
		return self._value_range

	@value_range.setter
	def value_range(self, values=array([0, 0, 0])):
		array_check_0 = array([0, 0, 0])
		array_check_1 = array([0, 0])

		if not isinstance(values, type(array)):
			raise TypeError('The unique tolerances must be handed in as an numpy matrix / array')

		elif (values.shape != array_check_0.shape or values.shape != array_check_1.shape) or \
				(values.ndim != array_check_0.ndim or values.ndim != array_check_1.ndim):
			raise ValueError('The array must be one dimensional with only 2 columns')

		elif values[0] != 0 or values[1] != 0 or values[2] != 0:
			self._value_range = values

		else:
			self._value_range = values

	#########################

	def update_value_range(self):
		"""Method to set / update the value range resulting from the tolerance(s) and nominal value of the variable."""
		##### TOLERANCE TYPE #####
		# Denotes the type of tolerance range, Default value of 0 is a plus or minus (+ve/-ve) type of tolerance,
		# 1 is purely positive (+ve) tolerance, and 2 is purely negative (-ve) tolerance.

		##### TOLERANCE PREFERENCE #####
		# What is the preferred tolerance value when nom_value is updated? Default (0) is percent tolerance.
		# 1 indicates that a fixed tolerance value is preferred

		if self._nom_value_set and (self._tol_value_set or self._tol_values_unique_set):

			if self._tol_values_unique_set:
				# There are unique values, i.e. there are different values for positive / negative tolerance

				if not self.tol_type == 0:
					raise ValueError("Tolerance type can only be 0 for unique tolerance values")

				elif not self._tol_values_unique_set:
					raise ValueError("Unique tolerance values are not set")

				else:  # Positive and Negative Tolerance (only possible case for unique tolerances)
					self._value_range = array([(self.nom_value + self.tol_values_unique[0]),  	# Maximal
											   self.nom_value,  								# Nominal
											   (self.nom_value - self.tol_values_unique[1])])  	# Minimal

			elif self._tol_value_set:
				# Positive / Negative values are the same, or there is only positive / negative tolerance

				if self.tol_type == 0:  # Positive and Negative Tolerance
					self._value_range = array([(self.nom_value + self.tol_value),  				# Maximal
											   self.nom_value,  								# Nominal
											   (self.nom_value - self.tol_value)])  			# Minimal

				elif self.tol_type == 1:  # Only Positive Tolerance
					self._value_range = array([(self.nom_value + self.tol_value),  				# Maximal
											   self.nom_value])  								# Nominal

				elif self.tol_type == 2:  # Only Negative Tolerance
					self._value_range = array([self.nom_value,  								# Nominal
											   (self.nom_value - self.tol_value)])  			# Minimal

		elif self.nom_value and not (self._tol_value_set or self._tol_values_unique_set):
			pass

		else:
			raise ValueError("Either a nominal, tolerance, or unique tolerance value has not been set.")
