import argparse

from axis.items.package import debug_package


def main() -> None:
    parser = argparse.ArgumentParser(description="Axis package debug runner")
    parser.add_argument(
        "--path",
        default="codebase/sandbox",
        help="Path to the package root",
    )
    args = parser.parse_args()
    debug_package(args.path)


if __name__ == "__main__":
    main()
