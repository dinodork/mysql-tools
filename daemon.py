"""Utility for creating a Deamon process (detached from tty)"""

import os


# pylint: disable=too-few-public-methods
class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """

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
                os.execv(self.executable, self.args)
                os._exit(1)

            os.waitpid(mysqld_pid, 0)
            os._exit(0)

        os.waitpid(child_pid, 0)
