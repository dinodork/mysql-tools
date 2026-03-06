import gdb


class KeyPrinter(gdb.Command):
    """Prints Hello, World!"""

    def __init__(self):
        super(KeyPrinter, self).__init__("pkey", gdb.COMMAND_USER)

    def invoke(self, argstr, from_tty):
        pos = 0
        args = [s.strip('" ') for s in argstr.split(",")]
        val = gdb.parse_and_eval(args[0])

        nullable = True
        for arg in args[1:]:
            if arg[0] == "$":
                arg = str(gdb.parse_and_eval(arg)).strip('" ')
            if arg.upper() == "NN" or arg.upper() == "NOT NULL":
                nullable = False

        if nullable:
            if val[0]:
                print("string: NULL")
                return
            else:
                pos += 1

        print(f"string of length {val[pos] + (int(val[pos + 1]) << 8)}:{val + pos + 2}")


KeyPrinter()
