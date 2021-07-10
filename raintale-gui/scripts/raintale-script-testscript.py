import argparse
import sys

parser = argparse.ArgumentParser(description="Find the sum of all the numbers below a certain number.")
parser.add_argument('--below', help='The number to find the sum of numbers below.', type=int, default=1000)

def main():
    args = parser.parse_args()
    s = sum((i for i in range(args.below)))
    print("Sum =", s)
    return 0

if __name__ == "__main__":
    sys.exit(main())
