#!/usr/bin/env python3

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Example script for a new skill")
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    print(output_dir)


if __name__ == "__main__":
    main()
