#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Generate a cryptographically secure bearer token for ``http_request_token``.

Usage:
    python tools/gen_token.py        # 32 random bytes (43 chars, 256-bit)
    python tools/gen_token.py 48     # optional: custom byte count
"""
import secrets
import sys


def main() -> int:
    nbytes = 32
    if len(sys.argv) > 1:
        nbytes = int(sys.argv[1])
    print(secrets.token_urlsafe(nbytes))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
