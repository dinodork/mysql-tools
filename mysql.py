"""Starts the MySQL server"""

import logging
import os
import subprocess
import sys

import psutil

from daemon import Daemon


def setup_logging(verbosity):
    """Configure logging based on verbosity level."""
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity >= 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(message)s")


# pylint: disable=too-few-public-methods
class Defaults:
    """Should probably be loaded from a file"""

    BUILD_HOME = "build"
    BUILD_TYPE = "debug"
    DATABASE = "mysql"
    DATADIR = "mydata"
    LOWER_CASE_TABLE_NAMES = 1
    PORT = 11211
    USER = "root"


class MySQL:
    """Base class for all mysql executables (client, server)"""

    def __init__(self, version, bindir, verbose):
        self.version = version
        self.bindir = bindir
        self.verbose = verbose
        logging.debug("mysql init w %s %s", bindir, verbose)


class Server(MySQL):
    """Represents the server binary"""

    def __init__(self, datadir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datadir = datadir
        self.executable = f"{self.bindir}/mysqld"

    def create_database(self, args: dict, mysqld_args: list):
        """Creates the database."""

        subprocess_args = [
            self.executable,
            f"--datadir={self.datadir}",
            "--initialize-insecure",
        ] + mysqld_args
        logging.info("Creating database in %s", self.datadir)
        if self.version["MYSQL_VERSION_MAJOR"] <= 5:
            subprocess_args += [
                f"--lc-messages-dir={self.bindir}/build/debug/sql/share/english",
            ]

        if args.dry_run:
            logging.info(
                "Would have run mysqld like this: %s", " ".join(subprocess_args)
            )
            return

        logging.info("Running mysqld like this: %s", " ".join(subprocess_args))

        try:
            subprocess.run(subprocess_args, check=True)
        except subprocess.CalledProcessError as err:
            logging.critical("Failed to create database: %s", err, file=sys.stderr)
            sys.exit(1)

    def get_pid(self):
        """Returns the pid of the mysqld process"""
        for proc in psutil.process_iter(["pid", "cmdline"]):
            try:
                if (
                    proc.info["cmdline"] is not None
                    and self.executable in proc.info["cmdline"]
                ):
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return None

    def start(self, args, mysqld_args):
        """Starts the mysqld process."""

        subprocess_args = [self.executable] + mysqld_args

        if args.dry_run:
            logging.info(
                "Would have run mysqld like this: %s", " ".join(subprocess_args)
            )
            return
        logging.info("Running mysqld like this: %s", " ".join(subprocess_args))

        if args.verbose >= 1:
            daemon = Daemon(
                self.executable, subprocess_args, stdout=sys.stdout, stderr=sys.stderr
            )
        else:
            devnull = open(os.devnull, "w", encoding=ascii)
            daemon = Daemon(
                self.executable, subprocess_args, stdout=devnull, stderr=devnull
            )
        daemon.daemonize()


class Client(MySQL):
    """Represents the client binary"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executable = f"{self.bindir}/mysql"

    def start(self, args, client_args):
        """Starts the MySQL client."""

        subprocess_args = [self.executable] + client_args

        if args.dry_run:
            logging.info(
                "Would have run mysql like this: %s", " ".join(subprocess_args)
            )
            return

        logging.info("Running mysql like this: %s", " ".join(subprocess_args))

        os.execv(self.executable, subprocess_args)


def determine_build_specifics(args) -> (str, str):
    """This is the complex part of these scripts. Basically, there are two
    modes of working. Either you specify the build type, in which case mysql
    gets built in `build/<build type>` under the source director. The other
    option is to specify the full build path (doesn't have to be absolute
    though)"""

    if args.build_dir:
        build_dir = args.build_dir
        logging.debug("--build-dir specified, setting build directory to %s", build_dir)
        return None, build_dir

    if args.build_type:
        build_type = args.build_type
        build_dir = f"{args.workdir}/build/{build_type}"
        logging.debug(
            "--build-type %s specified, setting build directory to %s",
            build_type,
            build_dir,
        )
        return build_type, build_dir

    build_type = Defaults.BUILD_TYPE
    build_dir = f"{args.workdir}/build/{build_type}"
    logging.debug(
        "Neither --build-type nor --build-dir specified, defaulting build type to "
        "%s and build directory to %s",
        build_type,
        build_dir,
    )
    return build_type, build_dir


def get_socket_path(version, build_type):
    """Generates a socket file name from the version and build type."""
    major_version = version["MYSQL_VERSION_MAJOR"]
    minor_version = version["MYSQL_VERSION_MINOR"]

    return f"/tmp/mysql-{major_version}.{minor_version}-{build_type}.sock"


def read_version(workdir):
    """Parses the version file to a dict."""
    version = {}
    found_version_file_name = None

    for version_file_name in ["MYSQL_VERSION", "VERSION"]:
        if os.path.isfile(f"{workdir}/{version_file_name}"):
            logging.debug("Found version file %s", version_file_name)
            found_version_file_name = version_file_name
            break

    if found_version_file_name is None:
        logging.critical(
            "Warning, can't find a version file in %s!",
            workdir,
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
        logging.critical(
            "Warning, failed to open %s in %s!",
            found_version_file_name,
            workdir,
        )
        raise
    return version


def get_bin_dir(version, build_dir):
    """The binary directory given version and build directory."""
    if version["MYSQL_VERSION_MAJOR"] < 8:
        return f"{build_dir}/sql"
    return f"{build_dir}/runtime_output_directory"


def get_mysqld_executable_path(version, build_dir):
    return f"{get_bin_dir(version, build_dir)}/mysqld"


def get_mysql_executable_path(version, build_dir):
    return f"{get_bin_dir(version, build_dir)}/mysql"
