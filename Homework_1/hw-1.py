import math

def print_type(variable):
    """This function prints the type of supplied variable

    Args:
        variable (Any): variable to print type for
    """
    for var in variable:
        print(type(var))


def do_action(variable):
    """Does the action depending on variable's type. (hint: you can either use print function right here,
    or return the result. For now it doesn't matter)
    Defined actions:
        int: square the number (x**2; pow(x,2); x*x)
        float: and π(pi) (from math.pi, don't forget the import~!) to it and print the result (+ pi?)
        bool: inverse it (e.g if you have True, make it False) and print the result (not var)
        list: print elements in reversed order (list(reversed(variables))

    Args:
        variable (Any): variable to perform action on
    """
    for var in variable:
        if isinstance(var, bool):
            print(not var)
        elif isinstance(var, int):
            print(pow(var, 2))
        elif isinstance(var, float):
            print(var + math.pi)
        elif isinstance(var, list):
            print(list(reversed(var)))
        else:
            print("Put some data already! (Though you won't see it..)")

variables = [ 42, 45.0, True, False, [16, 9, 43, 65, 97, 0]]

print("Data: ", variables, "\n")
print("Output of 'print_type' command:")
print_type(variables)
print("\nOutput of 'do_action' command:")
do_action(variables)
