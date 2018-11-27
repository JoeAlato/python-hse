# import argparse
# parser = argparse.ArgumentParser()
# parser.parse_args()

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("echo")
# args = parser.parse_args()
# print(args.echo)

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("echo", help="echo the string you use here")
# args = parser.parse_args()
# print(args.echo)

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("square", help="display a square of a given number")
# args = parser.parse_args()
# print(args.square**2)
# ## fix:
# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("square", help="display a square of a given number",
                    # type=int)
# args = parser.parse_args()
# print(args.square**2)

### OPTIONAL ARGUMENTS

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("--verbosity", help="increase output verbosity")
# args = parser.parse_args()
# if args.verbosity:
    # print("verbosity turned on")
	
# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("--verbose", help="increase output verbosity",
                    # action="store_true")
# args = parser.parse_args()
# if args.verbose:
   # print ("verbosity turned on")

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("square", type=int,
                    # help="display a square of a given number")
# parser.add_argument("-v", "--verbose", action="store_true",
                    # help="increase output verbosity")
# args = parser.parse_args()
# answer = args.square**2
# if args.verbose:
    # print( "the square of {} equals {}".format(args.square, answer))
# else:
    # print (answer)
	
	
# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("square", type=int,
                    # help="display a square of a given number")
# parser.add_argument("-v", "--verbosity", type=int,
                    # help="increase output verbosity")
# args = parser.parse_args()
# answer = args.square**2
# if args.verbosity == 2:
    # print("the square of {} equals {}".format(args.square, answer))
# elif args.verbosity == 1:
    # print( "{}^2 == {}".format(args.square, answer))
# else:
    # print (answer)
	
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("square", type=int,
                    help="display a square of a given number")
parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2],
                    help="increase output verbosity")
args = parser.parse_args()
answer = args.square**2
if args.verbosity == 2:
    print("the square of {} equals {}".format(args.square, answer))
elif args.verbosity == 1:
    print( "{}^2 == {}".format(args.square, answer))
else:
    print (answer)