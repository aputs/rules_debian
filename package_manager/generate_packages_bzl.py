#!/usr/bin/env python

import argparse
import json

from textwrap import dedent

parser = argparse.ArgumentParser(
    description="parse Packages.json and generate packages.bzl"
)

parser.add_argument(
    "--json-packages", nargs="+", default=[], help="A Packages.json files to use"
)
parser.add_argument("--workspace-name", action="store", help="workspace name")
parser.add_argument("--out", action="store", help="Write parsed Output to File")

INDEX_KEY = "Package"
FILENAME_KEY = "Filename"
SHA256_KEY = "SHA256"

# "libzmq3-dev": {
#   "Package": "libzmq3-dev",
#   "Source": "zeromq3",
#   "Version": "4.3.1-4+deb10u1",
#   "Installed-Size": "2414",
#   "Maintainer": "Laszlo Boszormenyi (GCS) <gcs@debian.org>",
#   "Architecture": "amd64",
#   "Replaces": "libzmq5-dev",
#   "Provides": "libzmq5-dev",
#   "Depends": "libzmq5 (= 4.3.1-4+deb10u1), libpgm-dev (>= 5.2.122~dfsg), libsodium-dev, libnorm-dev, libkrb5-dev",
#   "Conflicts": "libzmq-dev, libzmq5-dev",
#   "Description": "lightweight messaging kernel (development files)",
#   "Homepage": "https://www.zeromq.org/",
#   "Description-md5": "7b2c1e47f6d305566aebc0e65e04f5ee",
#   "Multi-Arch": "same",
#   "Section": "libdevel",
#   "Priority": "optional",
#   "Filename": "https://snapshot.debian.org/archive/debian-security/20190730T203253Z/pool/updates/main/z/zeromq3/libzmq3-dev_4.3.1-4+deb10u1_amd64.deb",
#   "Size": "441552",
#   "SHA256": "d6760915027c2f7fd728724c3a639e51589b3232d71fa689d2aef4c042df7741"
# }


def main():
    args = parser.parse_args()

    all_packages = {}

    for j in args.json_packages:
        with open(j, "r") as f:
            packages = json.load(f)
            for name, fields in packages.items():
                all_packages[name] = fields

    gen = dedent(
        """
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_file")

_WORKSPACE_NAME = '"""
        + args.workspace_name
        + """'
_ALL_PACKAGES = {
"""
        + ",\n".join(
            [
                "'" + name + "': '" + fields[FILENAME_KEY].split("/")[-1] + "'"
                for name, fields in all_packages.items()
            ]
        )
        + """
}

def _canon_name(name):
    return "%s__%s" % (_WORKSPACE_NAME, name.replace("+", "_"))

def package(name):
    if name not in _ALL_PACKAGES.keys():
        fail("unknown package `{}`".format(name))

    return "@" + _canon_name(name) + "//file:" + _ALL_PACKAGES[name]

def parse_package_list(**kwargs):

"""
    )

    for name, fields in all_packages.items():
        gen = gen + """
    http_file(
        name = _canon_name("{name}"),
        urls = ["{url}"],
        sha256 = "{sha256}",
        downloaded_file_path="{filename}",
    )
""".format(
            name=name,
            url=fields[FILENAME_KEY],
            sha256=fields[SHA256_KEY],
            filename=fields[FILENAME_KEY].split("/")[-1],
        )

    if args.out:
        with open(args.out, "w") as f:
            f.write(gen)


if __name__ == "__main__":
    main()
