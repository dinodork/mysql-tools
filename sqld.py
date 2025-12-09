"""Starts the MySQL server"""

import argparse
import os
import pathlib

import mysql


class ExpandPath(argparse.Action):
    """Because mysqld has this annoying habit of not expanding ~"""

    def __init__(self, *args, **kwargs):
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, option_string.replace("--", ""), values.expanduser())


def main():
    """Guts of the script"""

    parser = argparse.ArgumentParser(description="Starts mysqld and drops you into it.")

    mysqld_args = parser.add_argument_group("mysqld", "Passed verbatim to mysqld.")

    mysqld_args.add_argument("--port", type=int, default=mysql.PORT)
    mysqld_args.add_argument("--no-defaults", action="store_true")
    mysqld_args.add_argument("--lower-case-table-names", type=int, default=1)
    mysqld_args.add_argument(
        "--datadir",
        type=pathlib.Path,
        default=mysql.DEFAULT_DATADIR,
        action=ExpandPath,
        help="Passed to mysqld, but expands the `~' character.",
    )
    parser.add_argument("-B", "--build-dir", type=ascii)
    parser.add_argument(
        "-b", "--build-type", type=ascii, default=mysql.DEFAULT_BUILD_TYPE
    )

    args, unknown_args = parser.parse_known_args()

    os.makedirs(args.datadir, exist_ok=True)

    if args.build_dir:
        build_dir = args.build_dir
    else:
        # Black can't handle this line
        # fmt:off
        build_dir = f"build/{args.build_type.strip('\'')}"
        # fmt:on

    mysqld_executable = f"{build_dir}/runtime_output_directory/mysqld"

    # Remove all arguments that were meant only for this script
    del args.build_dir
    del args.build_type

    mysql.start_mysqld(mysqld_executable, args, unknown_args)


if __name__ == "__main__":
    main()
