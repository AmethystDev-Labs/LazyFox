import argparse

from cli.commands import init as init_command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lazyfox",
        description=(
            "LazyFox CLI\n"
            "用于从固定仓库 AmethystDev-Labs/LazyFox 下载 Release 源码。"
        ),
        epilog=(
            "示例:\n"
            "  lazyfox init\n"
            "  lazyfox init -v v0.1.0\n"
            "  lazyfox init -d ./LazyFox-New\n"
            "  lazyfox init -d ./LazyFox-New --force"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init",
        help="下载源码（latest 或指定版本）",
        description=(
            "从固定仓库下载源码:\n"
            "https://github.com/AmethystDev-Labs/LazyFox"
        ),
    )
    init_parser.add_argument(
        "--version",
        "-v",
        help="Release tag。默认 latest",
    )
    init_parser.add_argument(
        "--dest",
        "-d",
        default=".",
        help="下载并解压到的目录，默认当前目录",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已存在的同名文件",
    )
    init_parser.set_defaults(handler=init_command.run)

    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)
