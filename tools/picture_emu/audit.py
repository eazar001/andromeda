"""Run the full PICTURE comparison and print the results. Writes no game data."""
import argparse
from pathlib import Path

import checks
from emulator import PictureEmu, load_pens


def main():
    args = _parse_args()
    emu, pens = PictureEmu(args.game), load_pens(args.game)
    failed = _report_corpus(emu, pens, args.game)
    for name, pictures in checks.synthetic_families(args.seed):
        pictures = list(pictures)
        mismatches = checks.count_mismatches(emu, pens, pictures)
        failed |= mismatches > 0
        print(f"{name}: {len(pictures)} pictures, {mismatches} mismatches")
    total, differing = checks.showpic_line_diffs(pens, args.line_step)
    print(f"line rules, rules vs. showpic: {total} shapes, {differing} differ")
    return int(failed)


def _parse_args():
    default_game = Path(__file__).resolve().parents[2] / "test_games" / "sq1"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", type=Path, default=default_game)
    parser.add_argument("--seed", type=int, default=2917)
    parser.add_argument("--line-step", type=int, default=1, help="check every Nth line length")
    return parser.parse_args()


def _report_corpus(emu, pens, game):
    results = checks.game_corpus(emu, pens, game)
    for name, diff in results.items():
        print(f"{name}: {diff.pictures} pictures, {diff.differing_pictures} differ, "
              f"visual pixels {diff.visual_pixels}, priority pixels {diff.priority_pixels}")
    rules = results["rules"]
    return bool(rules.visual_pixels or rules.priority_pixels)


if __name__ == "__main__":
    raise SystemExit(main())
