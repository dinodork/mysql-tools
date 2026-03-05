import gdb


class KeyPrinter(gdb.Command):
    """Prints Hello, World!"""

    def __init__(self):
        super(KeyPrinter, self).__init__("pkey", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        val = gdb.parse_and_eval(arg)
        if val[0]:
            print("string: NULL")
        else:
            print(f"debug {val[1]} {val[2]}")
            print(f"string of length {val[1] + (int(val[2]) << 8)}:{val + 3}")


KeyPrinter()
