import argparse
import sys
import os

parser = argparse.ArgumentParser(description="Test Script -- Add two numbers")
parser.add_argument('--first', help='The number 1', type=int, default=1, required=True)
parser.add_argument('--second', help='The number 2', type=int, default=1, required=True)
#parser.add_argument('--third', help='Optional third arg', type=int, default=1, required=False)

def main():
    args = parser.parse_args()
    # print(args.first)
    # print(args.second)
    add = args.first + args.second
    import time
    #time.sleep(30)
    # with open("output.txt", "w") as f:
    # 	f.write("Sum of two numbers: " + str(add))
    print("Sum of two numbers: " + str(add))

if __name__ == "__main__":
    sys.exit(main())
    

