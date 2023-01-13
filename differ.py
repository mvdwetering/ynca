#!/usr/bin/env python3

import argparse
import logging
import re


def get_commands_from_file(filename):
    commands = {}
    with open(filename) as commandfile:
        for line in commandfile:

            line = re.sub(r"#.*", "", line)
            line = line.strip()

            match = re.match(
                r".*@(?P<subunit>.+?):(?P<function>.+?)=(?P<value>.*)", line
            )
            if match is not None:
                subunit = match.group("subunit")
                function = match.group("function")
                value = match.group("value")

                if subunit not in commands:
                    commands[subunit] = set()

                commands[subunit].add(function)
    return commands


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Compare 2 files containing YNCA commands, output will be the commands not available in reference."
    )

    parser.add_argument(
        "reference",
        help="Reference file to compare against.",
    )
    parser.add_argument(
        "other",
        help="File to compare.",
    )
    args = parser.parse_args()

    reference_commands = get_commands_from_file(args.reference)
    other_commands = get_commands_from_file(args.other)

    for subunit, functions in other_commands.items():
        for function in sorted(functions):
            try:
                if function not in reference_commands[subunit]:
                    print(f"@{subunit}:{function}")
            except KeyError:
                pass
