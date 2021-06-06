load("@subpar//:subpar.bzl", "par_binary")

py_binary(
    name = "parse_metadata",
    srcs = ["parse_metadata.py"],
    deps = ["@bazel_tools//third_party/py/six"],
)

py_test(
    name = "parse_metadata_test",
    size = "small",
    srcs = ["parse_metadata_test.py"],
    data = ["testdata/Packages.txt"],
    deps = [":parse_metadata"],
)
