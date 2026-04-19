"""Rich-based display helpers for diffs and env tables."""

from typing import List

from rich.console import Console
from rich.table import Table
from rich import box

from envoy.diff import EnvDiff, ChangeType
from envoy.masking import is_secret, mask_value

console = Console()

CHANGE_COLORS = {
    ChangeType.ADDED: 'green',
    ChangeType.REMOVED: 'red',
    ChangeType.MODIFIED: 'yellow',
    ChangeType.UNCHANGED: 'dim',
}

CHANGE_SYMBOLS = {
    ChangeType.ADDED: '+',
    ChangeType.REMOVED: '-',
    ChangeType.MODIFIED: '~',
    ChangeType.UNCHANGED: ' ',
}


def display_diff(diffs: List[EnvDiff], show_unchanged: bool = False, mask_secrets: bool = True) -> None:
    table = Table(box=box.SIMPLE, show_header=True, header_style='bold')
    table.add_column('', width=2)
    table.add_column('Key')
    table.add_column('Old Value')
    table.add_column('New Value')

    for diff in diffs:
        if diff.change == ChangeType.UNCHANGED and not show_unchanged:
            continue
        color = CHANGE_COLORS[diff.change]
        symbol = CHANGE_SYMBOLS[diff.change]

        old = diff.old_value or ''
        new = diff.new_value or ''
        if mask_secrets and is_secret(diff.key):
            old = mask_value(old) if old else ''
            new = mask_value(new) if new else ''

        table.add_row(
            f'[{color}]{symbol}[/{color}]',
            f'[{color}]{diff.key}[/{color}]',
            f'[{color}]{old}[/{color}]',
            f'[{color}]{new}[/{color}]',
        )

    console.print(table)
