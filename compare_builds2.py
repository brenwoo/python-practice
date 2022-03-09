#!/usr/bin/env python3
import argparse


def main():
    parser = argparse.ArgumentParser(description="Select board and build to compare.")
    parser.add_argument(
        "--board-full-list",
        required=True,
        help="The board which full test list you wish to compare",
        dest="board_full",
    )
    parser.add_argument(
        "--build-number",
        required=True,
        help="txt file of build to compare",
        dest="build_list",
    )
    args = parser.parse_args()

    try:
        with open(r"%s" % args.build_list, "r+") as f:
            compare_build = set(map(str.strip, f))
    except IOError:
        print("File not found")

    try:
        with open(r"file_diff.txt", "w") as missing_tests:
            pass
    except IOError:
        print("File not found")

    try:
        with open(r"%s" % args.board_full, "r") as f:
            compare_full = set(map(str.strip, f))
    except IOError:
        print("File not found")
    try:
        with open(r"file_diff.txt", "w") as f:
            f.write(str(compare_full.symmetric_difference(compare_build)))
    except IOError:
        print("File not found.")


if __name__ == "__main__":
    main()
