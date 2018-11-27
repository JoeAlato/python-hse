# definitions from a module can be imported into other modules or into the main module
# import fibo
# fibo.fib(1000)
# print(fibo.fib2(100))
# print(fibo.__name__)

# # There is a variant of the import statement that imports names from a module directly into the importing module’s symbol table.
# from fibo import fib, fib2
# fib(500)
#
# # There is even a variant to import all names that a module defines:
# from fibo import *
# fib(500)
#
# # If the module name is followed by as, then the name following as is bound directly to the imported module.
# import fibo as fib
# fib.fib(500)
#
# from fibo import fib as fibonacci
# fibonacci(500)

# import importlib; importlib.reload(modulename)

# import fibo, sys
# dir(fibo)