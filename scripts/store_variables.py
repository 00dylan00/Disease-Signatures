"""
Store Variables

This script is used to store variables in the current namespace.

Structure:
    1. Imports, Variables, Functions
    2. Get Variables Currently in Namespace
    3. Store Variables
    4. Generate File Defining Variables
"""

# 1. Imports, Variables, Functions

# imports
from IPython import get_ipython
import sys

# variables
_variable_types_interest = ["int", "float", "float64", "str", "list", "dict", "tuple", "set", "DataFrame", "Series", "ndarray"]
_store_variables_output_file = "variables.txt"

# functions

# 2. Get Variables Currently in Namespace
try:
    ipython = get_ipython()
    _store_variables_variables = ipython.run_line_magic("who_ls", " ".join(_variable_types_interest))
except Exception as e:
    print(f"Error retrieving variables: {e}")

# 3. Store Variables
try:
    ipython.run_line_magic("store", " ".join(_store_variables_variables))
    print(f"Stored {len(_store_variables_variables)} variables!")
except Exception as e:
    print(f"Error storing variables: {e}")

# 4. Generate File Defining Variables
try:
    with open(_store_variables_output_file, "w") as f:
        f.write("%store -r\nimport sys\n")
        for _store_variables_variables_element in _store_variables_variables:
            f.write(f"{_store_variables_variables_element} = globals()['{_store_variables_variables_element}']\n")
        f.write(f"for var in {_store_variables_variables}:\n")
        f.write("\tprint(f'{var}: {sys.getsizeof(globals()[var]) / (1024 * 1024):.2f} MB')\n")
    print(f"Generated file {_store_variables_output_file}!\nrun '%load {_store_variables_output_file}' in the next notebook to avoid Pylance warnings!")
except Exception as e:
    print(f"Error generating {_store_variables_output_file} file: {e}")

# Cleanup
try:
    del f, _variable_types_interest, _store_variables_variables_element, _store_variables_variables, ipython, _store_variables_output_file, get_ipython, sys
except NameError:
    pass
