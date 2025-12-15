"""Starts the MySQL client"""

import argparse
import os
import sys

import mysql


def main():
    """Guts of the script"""

    parser = argparse.ArgumentParser(
        description="Start the mysql client and drops you into it."
    )

    mysql_args = parser.add_argument_group("mysql options", "Passed verbatim to mysql.")

    mysql_args.add_argument("--socket", type=str)

    parser.add_argument("-u", "--user", default=mysql.DEFAULT_USER)
    parser.add_argument("-D", "--database", default=mysql.DEFAULT_DATABASE)
    parser.add_argument("-B", "--build-dir")
    parser.add_argument("-b", "--build-type", default=mysql.DEFAULT_BUILD_TYPE)

    args, unknown_args = parser.parse_known_args()

    if args.build_dir:
        build_dir = args.build_dir
    else:
        # Black can't handle this line
        # fmt:off
        build_dir = f"build/{args.build_type.strip('\'')}"
        # fmt:on

    # pylint: disable=duplicate-code
    try:
        version = mysql.read_mysql_version(os.getcwd())
    except OSError:
        print("Exiting")
        sys.exit(1)

    mysql_executable = mysql.get_mysql_executable_path(version, build_dir)

    if args.socket is None:
        args.socket = mysql.get_socket_name(version, args)

    # Remove all arguments that were meant only for this script
    del args.build_dir
    del args.build_type

    mysql.start_client(mysql_executable, args, unknown_args)


if __name__ == "__main__":
    main()
