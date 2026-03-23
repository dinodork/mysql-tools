"""Starts the MySQL client"""

import argparse
import os

import mysql


def main():
    """Guts of the script"""

    parser = argparse.ArgumentParser(
        description="Starts mysql client and drops you into it."
    )

    # pylint: disable=duplicate-code
    parser.add_argument(
        "-C",
        "--workdir",
        default=os.getcwd(),
        help="change to DIR before doing anything else",
    )

    mysql_args = parser.add_argument_group("mysql options", "Passed verbatim to mysql.")

    # All arguments added here must be manually added to mysql_args
    mysql_args.add_argument("--socket", type=str)
    mysql_args.add_argument("-u", "--user", default=mysql.Defaults.USER)
    mysql_args.add_argument("-D", "--database", default=mysql.Defaults.DATABASE)

    parser.add_argument("-B", "--build-dir")
    parser.add_argument("-b", "--build-type")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="don't actually start mysql, only print how it would have started and then exit",
    )

    # pylint: disable=duplicate-code
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        help="verbosity",
    )

    args, unknown_args = parser.parse_known_args()

    mysql.setup_logging(args.verbose)

    build = mysql.Build(args.workdir, args.build_dir, args.build_type)
    build_type = build.get_build_type()
    build_dir = build.build_dir

    mysql_args = [f"--user={args.user}", f"--database={args.database}"] + unknown_args

    client = mysql.Client(build)

    if args.socket:
        mysql_args += [f"--socket={args.socket}"]
    else:
        mysql_args += [f"--socket={client.make_socket_path()}"]

    client.start(args, mysql_args)


if __name__ == "__main__":
    main()
