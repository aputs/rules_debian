def _dpkg_list_impl(repository_ctx):
    repository_ctx.file("BUILD", """
package(default_visibility = ["//visibility:public"])
exports_files(["packages.bzl"])
""")

    if len(repository_ctx.attr.sources) == 0:
        fail("please specifiy at least one Packages.json")

    args = [
        repository_ctx.which("python"),
        str(repository_ctx.path(repository_ctx.attr._generator)),
        "--workspace-name",
        repository_ctx.name,
        "--out",
        str(repository_ctx.path("packages.bzl")),
        "--json-packages",
    ] + [str(repository_ctx.path(src_path)) for src_path in repository_ctx.attr.sources]

    pypath = ""
    result = repository_ctx.execute(args, environment = {
        "PYTHONPATH": pypath,
    })
    if result.return_code:
        fail("generator command failed: %s (%s)" % (result.stderr, " ".join([str(a) for a in args])))

_dpkg_list = repository_rule(
    _dpkg_list_impl,
    attrs = {
        "sources": attr.label_list(
            allow_files = True,
        ),
        "_generator": attr.label(
            default = ":generate_packages_bzl.py",
            allow_single_file = True,
        ),
    },
)

def _dpkg_src_impl(repository_ctx):
    sha256 = repository_ctx.attr.sha256
    packages_gz_url = repository_ctx.attr.packages_gz_url
    package_prefix = repository_ctx.attr.package_prefix
    mirror_url = repository_ctx.attr.url
    snapshot = repository_ctx.attr.snapshot
    distro = repository_ctx.attr.distro
    arch = repository_ctx.attr.arch

    if packages_gz_url and not package_prefix:
        fail("packages_gz_url and package_prefix must be specified or skipped at the same time.")

    if arch == "ppc64le":
        arch = "ppc64el"
    elif arch == "arm":
        arch = "armhf"

    if (not packages_gz_url) and (not mirror_url or not snapshot or not distro or not arch):
        fail("If packages_gz_url is not specified, all of mirror_url, snapshot, distro and arch must be specified.")

    if not packages_gz_url:
        packages_gz_url = "%s/debian/%s/dists/%s/main/binary-%s/Packages.gz" % (
            mirror_url,
            snapshot,
            distro,
            arch,
        )

    if packages_gz_url and "ppc64le" in packages_gz_url:
        packages_gz_url = packages_gz_url.replace("ppc64le", "ppc64el")
    elif packages_gz_url and "-arm/" in packages_gz_url:
        packages_gz_url = packages_gz_url.replace("-arm/", "-armhf/")

    repository_ctx.file("file/BUILD", """
package(default_visibility = ["//visibility:public"])
exports_files(["Packages.json", "os_release.tar"])
""")

    repository_ctx.download(
        url = packages_gz_url,
        sha256 = sha256,
        output = "Packages.gz",
    )

    args = [
        repository_ctx.which("python"),
        str(repository_ctx.path(repository_ctx.attr._generator)),
        "--package-file=" + str(repository_ctx.path("Packages.gz")),
        "--json-out=" + str(repository_ctx.path("file/Packages.json")),
        "--mirror-url=" + mirror_url,
        "--snapshot=" + snapshot,
        "--package-prefix=" + package_prefix,
    ]

    pypath = str(repository_ctx.path(Label("@bazel_tools//third_party/py/six:BUILD")).dirname)

    result = repository_ctx.execute(args, environment = {
        "PYTHONPATH": pypath,
    })
    if result.return_code:
        fail("parse_metadata command failed: %s (%s)" % (result.stderr, " ".join([str(a) for a in args])))

_dpkg_src = repository_rule(
    _dpkg_src_impl,
    attrs = {
        "url": attr.string(),
        "arch": attr.string(),
        "distro": attr.string(),
        "snapshot": attr.string(),
        "packages_gz_url": attr.string(),
        "package_prefix": attr.string(),
        "sha256": attr.string(),
        "_generator": attr.label(
            default = ":parse_metadata.py",
            allow_single_file = True,
        ),
    },
)

def dpkg_list(**kwargs):
    _dpkg_list(**kwargs)

def dpkg_src(**kwargs):
    _dpkg_src(**kwargs)
