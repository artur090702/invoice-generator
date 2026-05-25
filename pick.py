import sys
import termios
import tty


def choose(question, options):
    n = len(options)
    idx = 0

    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch += sys.stdin.read(2)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def render():
        sys.stdout.write(f'\x1b[{n}A')
        for i, opt in enumerate(options):
            prefix = '> ' if i == idx else '  '
            sys.stdout.write(f'\x1b[2K\r{prefix}{opt}\n')
        sys.stdout.flush()

    print(question)
    for i, opt in enumerate(options):
        prefix = '> ' if i == idx else '  '
        print(f'{prefix}{opt}')

    while True:
        key = getch()
        if key in ('\r', '\n'):
            return options[idx]
        elif key == '\x1b[A':
            idx = (idx - 1) % n
        elif key == '\x1b[B':
            idx = (idx + 1) % n
        elif key == '\x03':
            raise KeyboardInterrupt
        render()

def ask(question, multiline=False):
    print(question)
    if not multiline:
        return input('> ')

    print("Double enter to submit")
    lines = []
    while True:
        line = input()
        if line == '':
            break
        lines.append(line)

    return '\n'.join(lines)
