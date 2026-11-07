from logic import act, cond, if_, not_, program
from session import FIRST_RUN_FLAG, boot


def test_sq1_reaches_its_title_room(game_dir):
    m = boot(game_dir=game_dir).run(600)
    assert m.exit_code is None and m.var(0) == 67
    assert any(ch == ord("S") for ch, _ in m.text.values())


def test_synthetic_logic0_runs_every_cycle_and_quits(game_dir):
    code = program(
        if_(not_(cond("isset", FIRST_RUN_FLAG)), act("set", FIRST_RUN_FLAG) + act("assignn", 30, 7)),
        act("increment", 31),
        if_(cond("greatern", 31, 9), act("quit", 1)),
    )
    m = boot({0: code}, game_dir=game_dir).run(2000)
    assert m.exit_code == 0
    assert (m.var(30), m.var(31)) == (7, 10)
