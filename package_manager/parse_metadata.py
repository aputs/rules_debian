#!/usr/bin/env python

import os
import sys
import gzip
import argparse
import json
import re
import six

from contextlib import contextmanager

parser = argparse.ArgumentParser(description="parse Packages.gz and generate BUILD")

parser.add_argument("--package-file", action="store", help="A Packages.gz files to use")
parser.add_argument(
    "--json-out", action="store", help="Write parsed Output to json File"
)
parser.add_argument(
    "--build-out", action="store", help="Write parsed Output to BUILD File"
)
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
    "--workspace-name", action="store", default="", help="The workspace name"
)
parser.add_argument(
    "--package-prefix",
    action="store",
    default="",
    help="The prefix to prepend to the value of Filename key in the Packages.gz file.",
)

SEPARATOR = ":"


def parse_package_metadata(file, mirror_url, snapshot, package_prefix):
    """Takes a debian package list, changes the relative urls to absolute urls,
    and saves the resulting metadata as a json file"""

    current_entry = {}
    current_key = None
    while True:
        line = file.readline()
        if not line:
            break
        if isinstance(line, six.binary_type):
            line = line.decode("utf-8")
        line = line.rstrip()
        if line == "":
            yield current_entry
            current_entry = {}
            current_key = None
            continue

        if re.match(r"\s", line):
            if current_entry is None or current_key is None:
                raise Exception("Found incorrect indention on line:" + line)
            current_entry[current_key] += line.strip()
        elif SEPARATOR in line:
            (key, value) = line.split(SEPARATOR, 1)
            current_key = key.strip().lower().replace("-", "_")
            if current_key in current_entry:
                raise Exception(
                    "Duplicate key for package metadata:"
                    + current_key
                    + "\n"
                    + str(current_entry)
                )
            value = value.strip()
            # The Filename Key is a relative url pointing to the .deb package
            # Here, we're rewriting the metadata with the absolute urls,
            # which is a concatenation of the mirror + '/debian/' + relative_path
            if current_key == "filename":
                if package_prefix:
                    value = package_prefix + value
                else:
                    value = mirror_url + "/debian/" + snapshot + "/" + value
            current_entry[current_key] = value

        else:
            raise Exception("Valid line, but no delimiter or indentation:" + line)

    if current_entry:
        yield current_entry


@contextmanager
def opengzfile(package_file, *args, **kwargs):
    f = None
    try:
        _, file_extension = os.path.splitext(package_file)
        if ".gz" == file_extension:
            f = gzip.open(package_file, *args, **kwargs)
        else:
            f = open(package_file, *args, **kwargs)
        yield f
    finally:
        if f:
            f.close()


def main():
    args = parser.parse_args()

    @contextmanager
    def openoutfile():
        if args.json_out:
            with open(args.json_out, "w") as f:
                yield f
        else:
            yield sys.stdout

    with openoutfile() as out:
        with opengzfile(args.package_file) as f:
            for entry in parse_package_metadata(
                f, args.mirror_url, args.snapshot, args.package_prefix
            ):
                entry["__workspace_name"] = args.workspace_name
                json.dump(entry, out)
                out.write("\n")


if __name__ == "__main__":
    main()
