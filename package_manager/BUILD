py_binary(
    name = "parse_metadata",
    srcs = ["parse_metadata.py"],
    deps = ["@bazel_tools//third_party/py/six"],
)

py_test(
    name = "parse_metadata_test",
    size = "small",
    srcs = ["parse_metadata_test.py"],
    data = [
        "testdata/Packages.gz",
        "testdata/Packages.txt",
    ],
    deps = [":parse_metadata"],
)

py_binary(
    name = "generate_packages_bzl",
    srcs = ["generate_packages_bzl.py"],
    deps = ["@bazel_tools//third_party/py/six"],
)

py_test(
    name = "generate_packages_bzl_test",
    size = "small",
    srcs = ["generate_packages_bzl_test.py"],
    data = [
        "testdata/Packages.json",
    ],
    deps = [":generate_packages_bzl"],
)
