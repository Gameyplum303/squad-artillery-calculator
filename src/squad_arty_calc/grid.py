"""Convert between Squad grid strings (e.g. "B7-5-3") and (x, y) meters.

See README.md "Squad's grid system" and "Coordinate convention" sections.
"""

from dataclasses import dataclass

# Keypad numbers -> (column_offset, row_offset) within a 3x3 square.
# column_offset: 0=west third, 1=middle third, 2=east third
# row_offset:    0=north third, 1=middle third, 2=south third
# This matches a keyboard numpad: 7 8 9 / 4 5 6 / 1 2 3
KEYPAD_OFFSETS = {
    7: (0, 0), 8: (1, 0), 9: (2, 0),
    4: (0, 1), 5: (1, 1), 6: (2, 1),
    1: (0, 2), 2: (1, 2), 3: (2, 2),
}
OFFSETS_TO_KEYPAD = {v: k for k, v in KEYPAD_OFFSETS.items()}

DEFAULT_MAIN_SQUARE_SIZE_M = 300.0


@dataclass
class GridSystem:
    """Holds the square size for whichever map you're calculating for.

    Squad's main grid square is fixed at 300m on every map, so the
    default is correct for real use -- this stays a parameter mainly so
    it isn't hardcoded in every call site.
    """
    main_square_size_m: float = DEFAULT_MAIN_SQUARE_SIZE_M

    def parse(self, grid: str) -> tuple[float, float]:
        """Parse a grid string like "B7", "B7-5", or "B7-5-3" into
        (x, y) meters relative to the map's top-left corner (A1's
        northwest corner = origin (0, 0)). Returns the center of the
        smallest square the string specifies.
        """
        parts = grid.strip().upper().split("-")
        main = parts[0]
        col_index = ord(main[0]) - ord("A")
        row_index = int(main[1:]) - 1

        size = self.main_square_size_m
        x = col_index * size
        y = row_index * size

        for part in parts[1:]:
            col_off, row_off = KEYPAD_OFFSETS[int(part)]
            size /= 3
            x += col_off * size
            y += row_off * size

        return (x + size / 2, y + size / 2)

    def to_grid(self, x: float, y: float, precision: int = 3) -> str:
        """Inverse of parse(): turn (x, y) meters back into a grid
        string, to the given precision level (1 = main grid only,
        2 = +keypad, 3 = +sub-keypad).
        """
        size = self.main_square_size_m
        col_index = int(x // size)
        row_index = int(y // size)
        result = f"{chr(ord('A') + col_index)}{row_index + 1}"

        rem_x = x - col_index * size
        rem_y = y - row_index * size
        cur_size = size

        digits = []
        for _ in range(precision - 1):
            cur_size /= 3
            col_off = min(int(rem_x // cur_size), 2)
            row_off = min(int(rem_y // cur_size), 2)
            digits.append(OFFSETS_TO_KEYPAD[(col_off, row_off)])
            rem_x -= col_off * cur_size
            rem_y -= row_off * cur_size

        if digits:
            result += "-" + "-".join(str(d) for d in digits)
        return result
