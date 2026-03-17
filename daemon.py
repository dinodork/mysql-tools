"""Utility for creating a Deamon process (detached from tty)"""

import os


# pylint: disable=too-few-public-methods
class Daemon:
    """A generic daemon class."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        executable,
        args,
        stdin="/dev/null",
        stdout="/dev/null",
        stderr="/dev/null",
    ):
        self.executable = executable
        self.args = args
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def daemonize(self):
        """
        PID 1 in a Docker container may not reap orphans, so a plain double-fork
        leaves mysqld as a zombie when killed.  Instead we triple-fork: the
        grandchild stays alive as a minimal reaper that waitpid's mysqld.

        Python ──fork──▶ Child (exits immediately, reaped by Python)
                           └─setsid─fork──▶ Reaper (stays alive)
                                              └─fork──▶ mysqld (exec)

        For the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """

        saved_stdout = os.dup(self.stdout.fileno())
        saved_stderr = os.dup(self.stderr.fileno())

        child_pid = os.fork()
        if child_pid == 0:
            os.setsid()
            grandchild_pid = os.fork()
            if grandchild_pid > 0:
                os._exit(0)

            # Grandchild – the reaper.  Detach from the terminal.
            devnull = os.open(os.devnull, os.O_RDWR)
            os.dup2(devnull, 0)
            os.dup2(devnull, 1)
            os.dup2(devnull, 2)
            if devnull > 2:
                os.close(devnull)

            mysqld_pid = os.fork()
            if mysqld_pid == 0:
                # Restore stdout/stderr so mysqld output is visible.
                os.dup2(saved_stdout, 1)
                os.dup2(saved_stderr, 2)
                os.close(saved_stdout)
                os.close(saved_stderr)
                os.execv(self.executable, self.args)
                os._exit(1)

            os.close(saved_stdout)
            os.close(saved_stderr)
            os.waitpid(mysqld_pid, 0)
            os._exit(0)

        os.close(saved_stdout)
        os.close(saved_stderr)
        os.waitpid(child_pid, 0)
