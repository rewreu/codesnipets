import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--argument_name', type=str, default=None)

    args = parser.parse_args()

    if args.argument_name == "":
        print("Received an empty argument.")
    elif args.argument_name is None:
        print("Argument not provided.")
    else:
        print(f"Received argument: {args.argument_name}")

if __name__ == "__main__":
    main()
