#!/usr/bin/env python3
"""Minimal, dependency-free webhook forwarder for Cognis findings.

Reads JSON findings on stdin and POSTs them to a URL (SIEM/Slack/Jira bridge).
Usage:  <tool> scan . --format json | python integrations/webhook.py --url URL
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request


def _validate_url(url: str) -> str | None:
    """Return an error message if *url* is not a valid http/https URL, else None."""
    if not url:
        return "URL must not be empty."
    if not url.startswith(("http://", "https://")):
        return f"URL must start with http:// or https:// (got: {url!r})."
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Post JSON findings from stdin to a webhook URL."
    )
    ap.add_argument("--url", required=True, help="Destination http(s) URL.")
    ap.add_argument("--header", action="append", default=[], help="Key: Value")
    args = ap.parse_args(argv)

    url_error = _validate_url(args.url)
    if url_error:
        print(f"webhook error: {url_error}", file=sys.stderr)
        return 2

    raw = sys.stdin.read()
    if not raw.strip():
        print("webhook error: stdin was empty — nothing to post.", file=sys.stderr)
        return 2

    # Validate that the payload is well-formed JSON before sending.
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"webhook error: stdin is not valid JSON: {exc}", file=sys.stderr)
        return 2

    payload = raw.encode("utf-8")
    req = urllib.request.Request(args.url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    for h in args.header:
        k, sep, v = h.partition(":")
        if not sep or not k.strip():
            print(
                f"webhook error: malformed --header (expected 'Key: Value'): {h!r}",
                file=sys.stderr,
            )
            return 2
        req.add_header(k.strip(), v.strip())

    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"posted {len(payload)} bytes -> {r.status}")
        return 0
    except Exception as e:
        print(f"webhook error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
