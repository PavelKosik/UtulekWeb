#!/usr/bin/env python3
"""Nahradí v písmu Fraunces malé „j“ klidnějším tvarem.

Původní „j“ má pod účařím nožičku vybočenou doprava a zakroucený ocásek, takže ve velkých
nadpisech („Najděte svou…“) působí jako písmeno z jiného písma. Nové „j“ má rovnou nožičku
a ocásek převzatý z velkého „J“ téhož písma, zmenšený na šířku tahu malého „j“. Tečka,
horní patka, šířka znaku i kerning zůstávají původní. Úprava platí pro všechny tloušťky
(variabilní osa wght), kurzívy se netýká.

Spuštění:  python3 tools/fraunces_j.py   (potřebuje fontTools a brotli: pip install fonttools brotli)
Upraví assets/fonts/fraunces-normal-latin.woff2 na místě. Už upravené písmo nechá být,
takže po novém stažení písma z Google Fonts stačí skript pustit znovu.
Písmo je pod licencí SIL Open Font License 1.1, která úpravy povoluje.
"""
import pathlib
import sys

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.tables.TupleVariation import TupleVariation

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets/fonts/fraunces-normal-latin.woff2"

# Velké J: obrys od konce rovné části pravého okraje dříku (46) kolem ocásku po konec
# rovné části levého okraje (24).
J_RIGHT, J_LEFT = 46, 24
J_HOOK = list(range(J_RIGHT, 51)) + list(range(0, J_LEFT + 1))
# Malé j v původním písmu: 0 a 31 jsou konce rovného dříku, 1–30 ocásek,
# 32–49 levý okraj nahoru, patka a pravý okraj dolů, 50–61 tečka.
J_POINTS = 62


def masters(font, name):
    """Souřadnice znaku v nejtučnější (výchozí) a nejtenčí tloušťce."""
    glyf = font["glyf"]
    coords, ends, flags = glyf[name].getCoordinates(glyf)
    (var,) = font["gvar"].variations[name]
    light = [(x + dx, y + dy) for (x, y), (dx, dy) in zip(coords, var.coordinates)]
    return list(coords), light, list(flags), var


def new_j(big, small):
    """Ocásek z J zmenšený tak, aby jeho dřík měl šířku dříku malého j a sahal stejně hluboko."""
    scale = (small[0][0] - small[31][0]) / (big[J_RIGHT][0] - big[J_LEFT][0])
    big_bottom = min(big[i][1] for i in J_HOOK)
    small_bottom = min(y for x, y in small[:50])
    hook = [(small[31][0] + (big[i][0] - big[J_LEFT][0]) * scale,
             small_bottom + (big[i][1] - big_bottom) * scale) for i in J_HOOK]
    return [(round(x), round(y)) for x, y in hook + small[32:J_POINTS]]


def main():
    font = TTFont(FONT)
    glyf = font["glyf"]
    if len(glyf["j"].getCoordinates(glyf)[0]) != J_POINTS:
        print(FONT.name, "už má upravené j, nic neměním.")
        return
    big_bold, big_light, big_flags, _ = masters(font, "J")
    small_bold, small_light, small_flags, var = masters(font, "j")
    bold = new_j(big_bold, small_bold)
    light = new_j(big_light, small_light)

    hook = len(J_HOOK)
    flags = [big_flags[i] & 1 for i in J_HOOK] + [f & 1 for f in small_flags[32:J_POINTS]]
    flags[0] |= small_flags[0] & 0x40  # příznak překrývajících se obrysů

    glyph = glyf["j"]
    glyph.coordinates = GlyphCoordinates(bold)
    glyph.flags = bytearray(flags)
    glyph.endPtsOfContours = [hook + 18 - 1, len(bold) - 1]
    glyph.recalcBounds(glyf)
    deltas = [(lx - bx, ly - by) for (bx, by), (lx, ly) in zip(bold, light)]
    font["gvar"].variations["j"] = [TupleVariation(var.axes, deltas + list(var.coordinates[-4:]))]
    font["hmtx"]["j"] = (font["hmtx"]["j"][0], glyph.xMin)
    font.save(FONT)
    print(FONT.name, "upraveno: j má rovnou nožičku a ocásek podle J.")


if __name__ == "__main__":
    main()
