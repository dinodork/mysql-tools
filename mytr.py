"""Runs mysql-test-run from the root of the git clone"""

import os
import sys
import subprocess
from shutil import which

import mysql


def main():
    """All the work"""

    cwd = os.path.abspath(
        f"{mysql.Defaults.BUILD_HOME}/{mysql.Defaults.BUILD_TYPE}/mysql-test"
    )

    exe = f"{cwd}/mysql-test-run.pl"
    mtr_args = [exe] + sys.argv[1:]

    # If `colordiff` is available, pipe the test-run output through it.
    if which("colordiff"):
        with subprocess.Popen(
            mtr_args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        ) as p:
            with subprocess.Popen(["colordiff"], stdin=p.stdout) as cd:
                # Allow p to receive a SIGPIPE if colordiff exits.
                p.stdout.close()
                cd.wait()
                rc = cd.returncode
    else:
        with subprocess.Popen(mtr_args, cwd=cwd) as p:
            p.wait()
            rc = p.returncode

    sys.exit(rc)


if __name__ == "__main__":
    main()
