#!/usr/bin/env python3

import argparse
import os
import urllib
from urllib import request
from xml.dom import minidom

import util


def check_attachments(gnucash_file, base_path):
    doc = minidom.parseString(util.read(gnucash_file))

    slot_values = doc.getElementsByTagName("slot")

    file_paths = []

    for x in slot_values:
        slot_key = x.getElementsByTagName("slot:key")[0].firstChild.data

        if slot_key == "assoc_uri":
            rel_path = request.url2pathname(
                urllib.parse.urlparse(
                    x.getElementsByTagName("slot:value")[0].firstChild.data
                ).path
            )

            # remove leading slashes as this breaks os.path.join
            while rel_path[0] == "/":
                rel_path = rel_path[1:]

            file_paths.append(os.path.join(base_path, rel_path))

    errors = [x for x in file_paths if not os.path.exists(x)]

    return errors, file_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check whether all attached files are found"
    )
    parser.add_argument("gnucash_file")
    parser.add_argument("base_path")
    args = parser.parse_args()

    errors, file_paths = check_attachments(args.gnucash_file, args.base_path)

    print(
        "Found {} files to search in base path '{}'...".format(
            len(file_paths), args.base_path
        )
    )
    for e in errors:
        print("Failed to find {}...".format(e))
    print("Found {} errors in {} files!".format(len(errors), len(file_paths)))
