workspace(name = "rules_debian")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

## python dependencies

http_archive(
    name = "rules_python",
    sha256 = "778197e26c5fbeb07ac2a2c5ae405b30f6cb7ad1f5510ea6fdac03bded96cc6f",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_python/releases/download/0.2.0/rules_python-0.2.0.tar.gz",
        "https://github.com/bazelbuild/rules_python/releases/download/0.2.0/rules_python-0.2.0.tar.gz",
    ],
)

load("@rules_python//python:pip.bzl", "pip_parse")

http_archive(
    name = "subpar",
    sha256 = "b80297a1b8d38027a86836dbadc22f55dc3ecad56728175381aa6330705ac10f",
    strip_prefix = "subpar-2.0.0",
    urls = ["https://github.com/google/subpar/archive/refs/tags/2.0.0.tar.gz"],
)

http_archive(
    name = "rules_pkg",
    sha256 = "038f1caa773a7e35b3663865ffb003169c6a71dc995e39bf4815792f385d837d",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_pkg/releases/download/0.4.0/rules_pkg-0.4.0.tar.gz",
        "https://github.com/bazelbuild/rules_pkg/releases/download/0.4.0/rules_pkg-0.4.0.tar.gz",
    ],
)

load("@rules_pkg//:deps.bzl", "rules_pkg_dependencies")

rules_pkg_dependencies()

## docker dependencies

http_archive(
    name = "io_bazel_rules_docker",
    sha256 = "59d5b42ac315e7eadffa944e86e90c2990110a1c8075f1cd145f487e999d22b3",
    strip_prefix = "rules_docker-0.17.0",
    urls = ["https://github.com/bazelbuild/rules_docker/releases/download/v0.17.0/rules_docker-v0.17.0.tar.gz"],
)

load("@io_bazel_rules_docker//repositories:repositories.bzl", container_repositories = "repositories")

container_repositories()

pip_parse(
    name = "io_bazel_rules_docker_pip_deps",
    requirements_lock = "@io_bazel_rules_docker//repositories:requirements-pip.txt",
)

load("@io_bazel_rules_docker_pip_deps//:requirements.bzl", io_bazel_docker_install_deps = "install_deps")

io_bazel_docker_install_deps()

load("@io_bazel_rules_docker//repositories:deps.bzl", container_deps = "deps")

container_deps()

load("@io_bazel_rules_docker//python:image.bzl", _py_image_repos = "repositories")

_py_image_repos()

load("@io_bazel_rules_docker//container:container.bzl", "container_pull")

container_pull(
    name = "debian10",
    digest = "sha256:c33fbcd3f924892f2177792bebc11f7a7e88ccbc247f0d0a01a812692259503a",
    registry = "gcr.io",
    repository = "distroless/cc-debian10",
)

## debian dependencies

load("//package_manager:dpkg.bzl", "dpkg_list", "dpkg_src")

dpkg_src(
    name = "debian_buster",
    arch = "amd64",
    distro = "buster",
    sha256 = "bd1bed6b19bf173d60ac130edee47087203e873f3b0981f5987f77a91a2cba85",
    snapshot = "20190731T041823Z",
    url = "https://snapshot.debian.org/archive",
)

dpkg_src(
    name = "debian_buster_security",
    package_prefix = "https://snapshot.debian.org/archive/debian-security/20190730T203253Z/",
    packages_gz_url = "https://snapshot.debian.org/archive/debian-security/20190730T203253Z/dists/buster/updates/main/binary-amd64/Packages.gz",
    sha256 = "9ced04f06c2b4e1611d716927b19630c78fc7db604ba2cecebbb379cf6ba318b",
)

dpkg_list(
    name = "debian10_bundle",
    sources = [
        "@debian_buster//file:Packages.json",
        "@debian_buster_security//file:Packages.json",
    ],
)

load("@debian10_bundle//:packages.bzl", debian10_bundle_parse_package_list = "parse_package_list")

debian10_bundle_parse_package_list()
