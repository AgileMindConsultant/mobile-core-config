#!/usr/bin/env python3
"""CI guard for the PUBLIC config repo (spec 7.1).

Fails if any v1/*.json file: is invalid JSON; lacks schema_version == 1 or an
integer config_version >= 0; holds a key absent from registry.json (the vendored
ConfigKeys export); holds a wrong-typed or out-of-range value; or contains a
secret-shaped string (ad unit id, API key, token, e-mail, long opaque string).
"""
import glob
import json
import re
import sys

SECRET_RE = re.compile(
    r"ca-app-pub-|AIza[0-9A-Za-z_-]{20,}|ghp_|github_pat_|sk_live_|BEGIN [A-Z ]*PRIVATE KEY|"
    r"[\w.+-]+@[\w-]+\.[\w.]+|[A-Za-z0-9+/=_-]{32,}"
)


def strings(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)
    elif isinstance(value, str):
        yield value


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def main():
    registry = json.load(open("registry.json", encoding="utf-8"))["keys"]
    files = sorted(glob.glob("v1/*.json"))
    problems = []
    if not files:
        problems.append("no v1/*.json files")
    for path in files:
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except ValueError as e:
            problems.append("%s: invalid JSON (%s)" % (path, e))
            continue
        if not isinstance(doc, dict) or set(doc) != {"schema_version", "config_version", "values"}:
            problems.append("%s: root must have exactly schema_version, config_version, values" % path)
            continue
        if not is_int(doc["schema_version"]) or doc["schema_version"] != 1:
            problems.append("%s: schema_version must be 1" % path)
        if not is_int(doc["config_version"]) or doc["config_version"] < 0:
            problems.append("%s: config_version must be an integer >= 0" % path)
        if not isinstance(doc["values"], dict):
            problems.append("%s: values must be an object" % path)
            continue
        for key, value in doc["values"].items():
            meta = registry.get(key)
            if meta is None:
                problems.append("%s: key %r is not in the ConfigKeys registry" % (path, key))
                continue
            t = meta["type"]
            if t == "NUMBER":
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    problems.append("%s: %s must be a number" % (path, key))
                elif (meta.get("min") is not None and value < meta["min"]) or \
                        (meta.get("max") is not None and value > meta["max"]):
                    problems.append("%s: %s=%s outside [%s, %s]" % (path, key, value, meta.get("min"), meta.get("max")))
            elif t == "BOOL" and not isinstance(value, bool):
                problems.append("%s: %s must be a bool" % (path, key))
            elif t == "STRING" and not isinstance(value, str):
                problems.append("%s: %s must be a string" % (path, key))
            elif t == "JSON" and not isinstance(value, dict):
                problems.append("%s: %s must be an object" % (path, key))
        for s in strings(doc["values"]):
            if SECRET_RE.search(s):
                problems.append("%s: secret-shaped string %r" % (path, s[:24]))
    for p in problems:
        print("FAIL ", p)
    if problems:
        sys.exit(1)
    print("OK    %d file(s) valid against registry.json" % len(files))


main()
