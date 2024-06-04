"""Store Variables

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

# variables
_variable_types_interest = ["int", "float", "float64", "str", "list", "dict", "tuple", "set", "DataFrame", "Series"]
_store_variables_output_file = "variables.txt"
# functions

# 2. Get Variables Currently in Namespace
# get variables from current namespace
ipython = get_ipython()
_store_variables_variables = ipython.run_line_magic("who_ls"," ".join(_variable_types_interest))

# 3. Store Variables
# store variables with magic command store
ipython.run_line_magic(f"store", " ".join(_store_variables_variables))
print(f"Stored {len(_store_variables_variables)} variables!")

# 4. Generate File Defining Variables
# generate a file defining list of variables
# this is used to load variables in the next notebook
# so that Pylance doesn't start whining :)
with open("variables.txt", "w") as f:
    f.write("%store -r\n")
    for _store_variables_variables_element in _store_variables_variables:
        f.write(f"{_store_variables_variables_element} = globals()['{_store_variables_variables_element}']\n")
print(f"Generated file {_store_variables_output_file}!\nrun '%load {_store_variables_output_file}' in the next notebook to avoid Pylance warnings!")

        
del f, _variable_types_interest, _store_variables_variables_element, _store_variables_variables, ipython, _store_variables_output_file, get_ipython

