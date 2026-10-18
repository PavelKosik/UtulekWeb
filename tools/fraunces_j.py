#!/usr/bin/env python3
"""Nahradí v písmu Fraunces malé „j“ klidnějším tvarem.

Původní „j“ má pod účařím nožičku vybočenou doprava a ocásek zakroucený do velké kuličky,
takže ve velkých nadpisech („Najděte svou…“) působí jako písmeno z jiného písma. Nové „j“
má rovnou nožičku a ocásek bez kuličky: je to zrcadlově otočený ocásek „t“ téhož písma
(dřík „t“ má stejnou šířku jako dřík „j“), takže ladí se zbytkem abecedy. Tečka, horní
patka, šířka znaku i kerning zůstávají původní. Úprava platí pro všechny tloušťky
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

# Malé t: 37 a 19 jsou konce rovného levého a pravého okraje dříku, mezi nimi je ocásek.
# Po zrcadlení se body procházejí pozpátku, aby obrys dál vedl po směru hodinových ručiček.
T_LEFT, T_RIGHT = 37, 19
T_HOOK = list(range(T_LEFT, T_RIGHT - 1, -1))
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


def new_j(t, j):
    """Dřík j protažený rovně dolů a zakončený zrcadleným ocáskem t ve stejné hloubce jako dřív."""
    scale = (j[0][0] - j[31][0]) / (t[T_RIGHT][0] - t[T_LEFT][0])
    t_bottom = min(t[i][1] for i in T_HOOK)
    j_bottom = min(y for x, y in j[:50])
    hook = [(j[0][0] - (t[i][0] - t[T_LEFT][0]) * scale,
             j_bottom + (t[i][1] - t_bottom) * scale) for i in T_HOOK]
    return [(round(x), round(y)) for x, y in hook + j[32:J_POINTS]]


def main():
    font = TTFont(FONT)
    glyf = font["glyf"]
    if len(glyf["j"].getCoordinates(glyf)[0]) != J_POINTS:
        print(FONT.name, "už má upravené j, nic neměním.")
        return
    t_bold, t_light, t_flags, _ = masters(font, "t")
    j_bold, j_light, j_flags, var = masters(font, "j")
    bold = new_j(t_bold, j_bold)
    light = new_j(t_light, j_light)

    flags = [t_flags[i] & 1 for i in T_HOOK] + [f & 1 for f in j_flags[32:J_POINTS]]
    flags[0] |= j_flags[0] & 0x40  # příznak překrývajících se obrysů

    glyph = glyf["j"]
    glyph.coordinates = GlyphCoordinates(bold)
    glyph.flags = bytearray(flags)
    glyph.endPtsOfContours = [len(T_HOOK) + 18 - 1, len(bold) - 1]
    glyph.recalcBounds(glyf)
    deltas = [(lx - bx, ly - by) for (bx, by), (lx, ly) in zip(bold, light)]
    font["gvar"].variations["j"] = [TupleVariation(var.axes, deltas + list(var.coordinates[-4:]))]
    font["hmtx"]["j"] = (font["hmtx"]["j"][0], glyph.xMin)
    font.save(FONT)
    print(FONT.name, "upraveno: j má rovnou nožičku a ocásek jako t.")


if __name__ == "__main__":
    main()
