from foxdox_cli import FoxdoxCli


def main():
    app = FoxdoxCli()
    app.prompt = 'foxdox/> '
    app.cmdloop()


if __name__ == '__main__':
    main()
