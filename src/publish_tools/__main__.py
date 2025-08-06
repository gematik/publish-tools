import argparse
import os
from pathlib import Path

from .ig import publish
from .render import render_ig_list


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")

    publish_parser = subparsers.add_parser("publish", help="Publish project")
    publish_parser.add_argument(
        "--project-dir",
        type=Path,
        default=os.getcwd(),
        help="Path of the project to publish",
    )
    publish_parser.add_argument(
        "--ig-list",
        type=Path,
        required=True,
        help="IG list file to be updated",
    )

    render_list_parser = subparsers.add_parser(
        "render-list", help="Render the IG list file"
    )
    render_list_parser.add_argument(
        "--ig-list",
        type=Path,
        required=True,
        help="IG list file to render",
    )

    args = parser.parse_args()

    if args.cmd == "publish":
        publish(args.project_dir, args.ig_list)

    elif args.cmd == "render-list":
        render_ig_list(args.ig_list)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
