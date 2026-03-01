import argparse
import time

from rich import print

from axis import syn, val, items, src

def main() -> None:
    parser = argparse.ArgumentParser(description="Axis package debug runner")
    parser.add_argument(
        "--path",
        default="codebase/sandbox",
        help="Path to the package root",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch the source directory for changes",
    )
    args = parser.parse_args()

    pkg = items.Package.from_path(args.path)
    #print(pkg.database.entities_by_ref)

    # run some debug code to print out the contents of the package

    if args.watch:
        watch = src.SourceWatch(pkg.dir)
        watch.start()
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            watch.stop()


if __name__ == "__main__":
    main()
