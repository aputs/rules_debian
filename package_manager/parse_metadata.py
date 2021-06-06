#!/usr/bin/env python

import gzip
import argparse
import json
import re
import six

parser = argparse.ArgumentParser(description="parse Packages.gz and generate BUILD")

parser.add_argument("--package-file", action="store", help="A Packages.gz files to use")
parser.add_argument("--json-out", action="store", help="Write parsed Output to File")
parser.add_argument(
    "--mirror-url",
    action="store",
    default="",
    help="The base url for the package list mirror",
)
parser.add_argument(
    "--snapshot", action="store", default="", help="The snapshot date to download"
)
parser.add_argument(
    "--package-prefix",
    action="store",
    default="",
    help="The prefix to prepend to the value of Filename key in the Packages.gz file.",
)

INDEX_KEY = "Package"
FILENAME_KEY = "Filename"
SEPARATOR = ":"


def parse_package_metadata(data, mirror_url, snapshot, package_prefix):
    """Takes a debian package list, changes the relative urls to absolute urls,
    and saves the resulting metadata as a json file"""

    # this is called with the output of gzip.open, but should be strings
    if isinstance(data, six.binary_type):
        data = data.decode("utf-8")

    raw_entries = [line.rstrip() for line in data.splitlines()]
    parsed_entries = {}
    current_key = None
    current_entry = {}

    for line in raw_entries:
        if line:
            # If the line starts with indentation,
            # it is a continuation of the previous key
            if re.match(r"\s", line):
                if current_entry is None or current_key is None:
                    raise Exception("Found incorrect indention on line:" + line)
                current_entry[current_key] += line.strip()
            elif SEPARATOR in line:
                (key, value) = line.split(SEPARATOR, 1)
                current_key = key.strip()
                if current_key in current_entry:
                    raise Exception(
                        "Duplicate key for package metadata:"
                        + current_key
                        + "\n"
                        + str(current_entry)
                    )
                current_entry[current_key] = value.strip()
            else:
                raise Exception("Valid line, but no delimiter or indentation:" + line)
        else:
            if current_entry:
                parsed_entries[current_entry[INDEX_KEY]] = current_entry
            current_entry = {}
            current_key = None

    if current_entry:
        parsed_entries[current_entry[INDEX_KEY]] = current_entry

    # The Filename Key is a relative url pointing to the .deb package
    # Here, we're rewriting the metadata with the absolute urls,
    # which is a concatenation of the mirror + '/debian/' + relative_path
    for pkg_data in six.itervalues(parsed_entries):
        if package_prefix:
            pkg_data[FILENAME_KEY] = package_prefix + pkg_data[FILENAME_KEY]
        else:
            pkg_data[FILENAME_KEY] = (
                mirror_url + "/debian/" + snapshot + "/" + pkg_data[FILENAME_KEY]
            )

    return parsed_entries


def main():
    args = parser.parse_args()

    data = ""
    try:
        with gzip.open(args.package_file, "rb") as f:
            data = f.read()
    except IOError:
        with open(args.package_file, "rb") as f:
            data = f.read()

    metadata = parse_package_metadata(
        data, args.mirror_url, args.snapshot, args.package_prefix
    )

    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(metadata, f, indent=2)
    else:
        print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
