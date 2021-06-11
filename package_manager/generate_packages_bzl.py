#!/usr/bin/env python

import argparse
import json
import six
import sys
import re

from contextlib import contextmanager

parser = argparse.ArgumentParser(
    description="parse Packages.json and generate packages.bzl"
)

parser.add_argument(
    "--json-packages", nargs="+", default=[], help="A Packages.json files to use"
)
parser.add_argument("--workspace-name", action="store", help="workspace name")
parser.add_argument("--out", action="store", help="Write parsed Output to File")

PACKAGE_KEY = "package"
FILENAME_KEY = "filename"
VERSION_KEY = "version"
SHA256_KEY = "sha256"

# {
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


def read_packages_json(workspace_name, filenames):
    for filename in filenames:
        with open(filename, "rb") as f:
            for line in f:
                if isinstance(line, six.binary_type):
                    line = line.decode("utf-8")
                line = line.rstrip()
                entry = json.loads(line)
                entry["workspace-name"] = workspace_name
                yield entry


def resolve_packages(workspace_name, filenames):
    all_packages = {}

    for package in read_packages_json(workspace_name, filenames):
        name = package[PACKAGE_KEY]
        version = package[VERSION_KEY]
        sha256 = package[SHA256_KEY]
        location = package[FILENAME_KEY]
        filename = location.split("/")[-1]
        package_workspace_name = package["__workspace_name"]
        target_workspace = package_workspace_name + "__" + name + "__" + version
        resolved = {
            "location": location,
            "version": version,
            "sha256": sha256,
            "filename": filename,
            "target_workspace": re.sub(r"[^.a-zA-Z0-9-_]", "_", target_workspace),
        }

        all_packages[name] = all_packages.get(name, [])
        all_packages[name].append(resolved)

    return all_packages


@contextmanager
def _openfilename_or_stdout(filename, *args, **kwargs):
    try:
        with open(filename, *args, **kwargs) as f:
            yield f
            f.close()
    except:
        yield sys.stdout


def main():
    args = parser.parse_args()

    all_packages = resolve_packages(args.workspace_name, args.json_packages)

    with _openfilename_or_stdout(args.out, "w") as out:
        out.write(
            """load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_file")\n\n"""
        )
        out.write("ALL_PACKAGES = ")
        json.dump(all_packages, out)
        out.write("\n\n")
        out.write(
            """
def package(name):
    if name not in ALL_PACKAGES:
        fail("unknown package `{}`".format(name))
    entry = ALL_PACKAGES[name][0]
    return "@" + entry["target_workspace"] + "//file:" + entry["filename"]

def parse_package_list():
            """
        )

        for _, packages in all_packages.items():
            for package in packages:
                out.write(
                    """
    http_file(
        name = "{name}",
        urls = ["{location}"],
        sha256 = "{sha256}",
        downloaded_file_path="{filename}",
    )
                """.format(
                        name=package["target_workspace"],
                        location=package["location"],
                        sha256=package["sha256"],
                        filename=package["filename"],
                    )
                )


if __name__ == "__main__":
    main()
