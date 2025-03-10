"""Sources Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import argparse
import json
import logging
from typing import List, Dict

# IMPORTATION THIRDPARTY
from prompt_toolkit.completion import NestedCompleter

# IMPORTATION INTERNAL
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.helper_funcs import parse_simple_args

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


class SourcesController(BaseController):
    """Sources Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "get",
        "set",
    ]
    PATH = "/sources/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.commands_with_sources = dict()
        with open("data_sources_default.json") as f:
            self.json_doc = json.load(f)
            for context in self.json_doc:
                for menu in self.json_doc[context]:
                    if isinstance(self.json_doc[context][menu], Dict):
                        for submenu in self.json_doc[context][menu]:
                            if isinstance(self.json_doc[context][menu][submenu], Dict):
                                for subsubmenu in self.json_doc[context][menu][submenu]:
                                    self.commands_with_sources[
                                        f"{context}_{menu}_{submenu}_{subsubmenu}"
                                    ] = self.json_doc[context][menu][submenu][
                                        subsubmenu
                                    ]
                            else:
                                self.commands_with_sources[
                                    f"{context}_{menu}_{submenu}"
                                ] = self.json_doc[context][menu][submenu]
                    else:
                        self.commands_with_sources[f"{context}_{menu}"] = self.json_doc[
                            context
                        ][menu]

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["get"] = {c: None for c in list(self.commands_with_sources.keys())}
            choices["set"] = {c: None for c in list(self.commands_with_sources.keys())}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("sources/")
        mt.add_info("_info_")
        mt.add_cmd("get")
        mt.add_cmd("set")

        console.print(text=mt.menu_text, menu="Data Sources")

    @log_start_end(log=logger)
    def call_get(self, other_args):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="get",
            description="Get sources associated with a command and the one selected by default, using 'get <command>'.",
        )
        parser.add_argument(
            "-c",
            "--cmd",
            action="store",
            dest="cmd",
            choices=list(self.commands_with_sources.keys()),
            help="Command that we want to check the available data sources and the default one.",
            metavar="COMMAND",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            console.print(
                f"\n[param]Default   :[/param] {self.commands_with_sources[ns_parser.cmd][0]}"
            )
            console.print(
                f"[param]Available :[/param] {', '.join(self.commands_with_sources[ns_parser.cmd])}\n"
            )

    # pylint: disable=R0912
    @log_start_end(log=logger)
    def call_set(self, other_args):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="set",
            description="Set a default data sources associated with a command, using 'set <command> <source>'.",
        )
        parser.add_argument(
            "-c",
            "--cmd",
            action="store",
            dest="cmd",
            choices=list(self.commands_with_sources.keys()),
            help="Command that we to select the default data source.",
            metavar="COMMAND",
        )
        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="source",
            type=str,
            help="Data source to use by default on specified command.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
            if "-s" not in other_args and "--source" not in other_args:
                other_args.insert(2, "-s")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            menus = ns_parser.cmd.split("_")
            num_menus = len(menus)

            success = True
            valid_sources = list()

            # Update dictionary
            if num_menus == 1:
                if ns_parser.source not in self.json_doc[menus[0]]:
                    success = False
                    valid_sources = self.json_doc[menus[0]]
                else:
                    self.json_doc[menus[0]] = unique(
                        [ns_parser.source] + self.json_doc[menus[0]]
                    )
            elif num_menus == 2:
                if ns_parser.source not in self.json_doc[menus[0]][menus[1]]:
                    success = False
                    valid_sources = self.json_doc[menus[0]][menus[1]]
                else:
                    self.json_doc[menus[0]][menus[1]] = unique(
                        [ns_parser.source] + self.json_doc[menus[0]][menus[1]]
                    )
            elif num_menus == 3:
                if ns_parser.source not in self.json_doc[menus[0]][menus[1]][menus[2]]:
                    success = False
                    valid_sources = self.json_doc[menus[0]][menus[1]][menus[2]]
                else:
                    self.json_doc[menus[0]][menus[1]][menus[2]] = unique(
                        [ns_parser.source] + self.json_doc[menus[0]][menus[1]][menus[2]]
                    )
            elif num_menus == 4:
                if (
                    ns_parser.source
                    not in self.json_doc[menus[0]][menus[1]][menus[2]][menus[3]]
                ):
                    success = False
                    valid_sources = self.json_doc[menus[0]][menus[1]][menus[2]][
                        menus[3]
                    ]
                else:
                    self.json_doc[menus[0]][menus[1]][menus[2]][menus[3]] = unique(
                        [ns_parser.source]
                        + self.json_doc[menus[0]][menus[1]][menus[2]][menus[3]]
                    )

            if success:
                try:
                    with open("data_sources_default.json", "w") as f:
                        json.dump(self.json_doc, f, indent=4)
                    console.print(
                        "[green]The data source was specified successfully.\n[/green]"
                    )
                    # Update dictionary so if we "get" the change is reflected
                    for context in self.json_doc:
                        for menu in self.json_doc[context]:
                            if isinstance(self.json_doc[context][menu], Dict):
                                for submenu in self.json_doc[context][menu]:
                                    if isinstance(
                                        self.json_doc[context][menu][submenu], Dict
                                    ):
                                        for subsubmenu in self.json_doc[context][menu][
                                            submenu
                                        ]:
                                            self.commands_with_sources[
                                                f"{context}_{menu}_{submenu}_{subsubmenu}"
                                            ] = self.json_doc[context][menu][submenu][
                                                subsubmenu
                                            ]
                                    else:
                                        self.commands_with_sources[
                                            f"{context}_{menu}_{submenu}"
                                        ] = self.json_doc[context][menu][submenu]
                            else:
                                self.commands_with_sources[
                                    f"{context}_{menu}"
                                ] = self.json_doc[context][menu]
                except Exception as e:
                    console.print(
                        f"[red]Failed to write preferred data sources to file: "
                        f"{obbff.PREFERRED_DATA_SOURCE_FILE}[/red]"
                    )
                    console.print(f"[red]{e}[/red]")
            else:
                console.print(
                    f"[red]The data source selected is not valid, select one from: {', '.join(valid_sources)}.\n[/red]"
                )
