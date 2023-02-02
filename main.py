#!/usr/bin/python3
# coding:utf-8

import argparse

import utils
from metadata import *


def option():
    parser = argparse.ArgumentParser(description="Forensics tool")
    parser.add_argument(
        "-t", "--type", dest="type", help="Type of file", choices=["pdf", "img", "db"]
    )
    parser.add_argument(
        "-p", "--path", dest="path", help="Path of file", required=False
    )
    parser.add_argument(
        "-s",
        "--string",
        dest="string",
        help="More detailed metadata",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--exif",
        dest="exif",
        help="Image path for getting exif metadata",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--gps",
        dest="gps",
        help="Get GPS\'s coordinates",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--hist",
        dest="history",
        help="Get info in Firefox with file *.sqlite. c for cookies, p for places",
        required=False,
        choices=["c", "p"],
    )
    parser.add_argument(
        "--option",
        dest="option",
        help="Choice for drawing history result",
        required=False,
        choices=["html"],
    )

    return parser.parse_args()


def main():

    args = option()
    filename = str(args.path).rsplit("/", 1)

    if args.type == "pdf":
        print(f"[*] Try to found metadata on: {filename[1]}")
        if args.string:
            result = get_meta_with_regex(args.path)
            print(result)
        else:
            result = get_meta(args.path)
            for item in result:
                print(item)
    elif args.type == "img":
        print(f"[*] Try to found EXIF on: {filename[1]}")
        if args.exif:
            result = get_exif(args.path)
            utils.print_result(result[0], result[1])
        if args.gps:
            print(f"[*] Try to found GPS coordinates on: {filename[1]}")
            result = get_gps_coordinate(args.path)
            utils.print_result(result[0], result[1])

    elif args.type == "db":
        opt = args.option if args.option == "html" else None
        result = get_firefox_info(args.history, args.path, option=opt)
        utils.print_result(result[0], result[1])


if __name__ == "__main__":
    main()
