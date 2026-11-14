#!/usr/bin/env python3
"""Build a Meitrack command and print its bytes.

Defaults come from env vars MEITRACK_IMEI, MEITRACK_DIRECTION and
MEITRACK_DATA_ID; CLI options override them.
"""

import argparse
import os
import sys

from meitrack import CommandBuilder


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--imei", default=os.environ.get("MEITRACK_IMEI"))
    p.add_argument("--direction", default=os.environ.get("MEITRACK_DIRECTION", "@@"))
    p.add_argument("--data-id", default=os.environ.get("MEITRACK_DATA_ID", "a"))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("request-location")
    sub.add_parser("format-sdcard")
    sub.add_parser("restart-gsm")
    sub.add_parser("restart-gps")
    d = sub.add_parser("delete-file")
    d.add_argument("name")
    o = sub.add_parser("set-output-pin")
    o.add_argument("--speed", type=int, default=1)
    o.add_argument("--pin", type=int, default=0)
    o.add_argument("--state", type=int, default=2)
    args = p.parse_args(argv)
    if not args.imei:
        p.error("IMEI required (--imei or MEITRACK_IMEI)")
    return args


def main(argv=None):
    args = parse_args(argv)
    builder = CommandBuilder(
        args.imei.encode(), args.direction.encode(), args.data_id.encode()
    )
    if args.cmd == "delete-file":
        msg = builder.delete_file(args.name.encode())
    elif args.cmd == "set-output-pin":
        msg = builder.set_output_pin(args.speed, args.pin, args.state)
    else:
        msg = getattr(builder, args.cmd.replace("-", "_"))()
    if msg is None:
        print("invalid arguments", file=sys.stderr)
        return 1
    print(msg.as_bytes())
    return 0


if __name__ == "__main__":
    sys.exit(main())
