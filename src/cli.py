#!/usr/bin/env python3
import argparse

def main():
    parser = argparse.ArgumentParser(description="iPhone allocation simulator (skeleton)")
    parser.add_argument("--hello", action="store_true", help="test run")
    args = parser.parse_args()
    if args.hello:
        print("Hello, world. Skeleton OK.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
