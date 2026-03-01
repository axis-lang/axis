import argparse
from rich import print
from axis import syn, val, items

def main() -> None:
    parser = argparse.ArgumentParser(description="Axis package debug runner")
    parser.add_argument(
        "--path",
        default="codebase/sandbox",
        help="Path to the package root",
    )
    args = parser.parse_args()

    pkg = items.Package.from_path(args.path)
    #print(pkg.database.entities_by_ref)

    # run some debug code to print out the contents of the package


if __name__ == "__main__":
    main()
