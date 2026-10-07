import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print("Preview: would clear rebuildable cache" if args.dry_run else "Apply requested")


if __name__ == "__main__":
    main()
