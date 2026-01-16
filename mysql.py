"""Starts the MySQL server"""

import subprocess
import sys
import os


# pylint: disable=too-few-public-methods
class Defaults:
    """Should probably be loaded from a file"""

    BUILD_TYPE = "debug"
    DATABASE = "mysql"
    DATADIR = "mydata"
    LOWER_CASE_TABLE_NAMES = 2
    PORT = 11211
    USER = "root"


def determine_build_specifics(args):
    """This is the complex part of these scripts. Basically, there are two
    modes of working. Either you specify the build type, in which case mysql
    gets built in `build/<build type>` under the source director. The other
    option is to specify the full build path (doesn't have to be absolute
    though)"""

    if not args.build_dir and not args.build_type:
        build_type = Defaults.BUILD_TYPE
        build_dir = f"build/{build_type}"
        if args.verbose >= 1:
            print(
                "Neither --build-type nor --build-dir specified, defaulting build type to "
                f"{build_type} and build directory to {build_dir}"
            )
    elif args.build_type:
        build_type = args.build_type
        build_dir = f"build/{build_type}"
        if args.verbose >= 1:
            print(
                f"--build-type {build_type} specified, setting build directory to {build_dir}"
            )
    elif args.build_dir:
        build_dir = args.build_dir
        if args.verbose >= 1:
            print(f"--build-dir specified, setting build directory to {build_dir}")

    return build_type, build_dir


def get_socket_path(version, build_type):
    """Generates a socket file name from the version and build type."""
    major_version = version["MYSQL_VERSION_MAJOR"]
    minor_version = version["MYSQL_VERSION_MINOR"]

    return f"/tmp/mysql-{major_version}.{minor_version}-{build_type}.sock"


def read_mysql_version(args, workdir):
    """Parses the version file to a dict."""
    version = {}
    found_version_file_name = None

    for version_file_name in ["MYSQL_VERSION", "VERSION"]:
        if os.path.isfile(version_file_name):
            if args.verbose >= 1:
                print(f"Found version file {version_file_name}")
            found_version_file_name = version_file_name
            break

    if found_version_file_name is None:
        print(
            f"Warning, can't find a version file in {workdir}!",
            file=sys.stderr,
        )

    try:
        with open(
            f"{workdir}/{found_version_file_name}", "r", encoding="ascii"
        ) as version_file:
            for line in version_file:
                data = line.split("=")
                value = data[1].strip()
                version[data[0]] = int(value) if value.isdigit() else value
    except FileNotFoundError:
        print(
            f"Warning, failed to open {found_version_file_name} in {workdir}!",
            file=sys.stderr,
        )
        raise
    return version


def get_mysqld_executable_path(version, build_dir):
    """The full executable path of mysqld given version and build directory."""
    if version["MYSQL_VERSION_MAJOR"] < 8:
        return f"{build_dir}/sql/mysqld"
    return f"{build_dir}/runtime_output_directory/mysqld"


def get_mysql_executable_path(version, build_dir):
    """The full executable path of mysqld given version and build directory."""
    if version["MYSQL_VERSION_MAJOR"] < 8:
        return f"{build_dir}/client/mysql"
    return f"{build_dir}/runtime_output_directory/mysql"


def create_database(version, executable, datadir, workdir, args):
    """Creates the database."""

    subprocess_args = [executable, f"--datadir={datadir}", "--initialize-insecure"]
    if args.verbose >= 1:
        print(f"Creating database in {datadir}")
    if version["MYSQL_VERSION_MAJOR"] <= 5:
        subprocess_args += [
            f"--lc-messages-dir={workdir}/build/debug/sql/share/english",
        ]

    if args.dry_run:
        print(f"Would have run mysqld like this: {" ".join(subprocess_args)}")
        return

    print(f"Running mysqld like this: {" ".join(subprocess_args)}")

    subprocess.run(subprocess_args, check=True)


def start_mysqld(executable, args, mysqld_args):
    """Starts the mysqld process."""

    subprocess_args = [executable] + mysqld_args

    if args.dry_run:
        print(f"Would have run mysqld like this: {" ".join(subprocess_args)}")
        return
    print(f"Running mysqld like this: {" ".join(subprocess_args)}")

    # pylint: disable=consider-using-with
    subprocess.Popen(subprocess_args)


def start_client(executable, args, client_args):
    """Starts the MySQL client."""

    subprocess_args = [executable] + client_args

    if args.dry_run:
        print(f"Would have run mysql like this: {" ".join(subprocess_args)}")
        return
    print(f"Running mysql like this: {" ".join(subprocess_args)}")

    os.execv(executable, subprocess_args)
