"""Runtime results the wiki now cites. Each test names the claim it pins down."""
import pytest

import scenarios as s


@pytest.fixture(autouse=True)
def _needs_game(game_dir):
    pass


def test_end_of_loop_flag_comes_from_move_obj_x():
    r = s.end_of_loop_shares_parameter_1()
    assert r["flag80"] and not r["flag100"]


def test_step_time_zero_steps_without_motion_pass():
    r = s.step_time_zero()
    assert r["move_t0"][-1]["x"] > 70 and r["move_t1"][-1]["x"] == 70
    assert {x["loop"] for x in r["east_t0"][1:]} == {2} and r["east_t1"][-1]["loop"] == 0


def test_control_rows_survive_a_cel_and_water_takes_its_priority():
    rows = s.cel_over_control_rows()["priority_15"]["rows"][0]
    assert [rows[y][0] for y in (100, 101, 102, 103)] == ["01", "11", "21", "F1"]


def test_get_priority_lags_position():
    r = s.get_priority_after_position()
    assert r["before"] == r["straight_after"] != r["two_cycles_later"]


def test_save_file_layout_and_restore():
    r = s.save_file_bytes()
    assert r["block_lengths"][:4] == [1505, 774, 328, 100] and r["id_at_33"] == "SQ"
    assert r["size"] == 2748 + r["block_lengths"][4]
    assert r["logic0_runs_cycle_var220_flag220_flag12"][-1] == (3, 42, True, True)


def test_trace_on_twice_skips_a_byte():
    r = s.trace_on_twice()
    assert (r["var17"], r["var18"]) == (0x10, 0xF0)


def test_menu_choice_arrives_in_the_cycle_after_menu_input():
    r = s.menu_delivery_and_look()
    assert r["menu_opened_at_cycle"] == [4] and r["controller5_seen_at_cycle"] == 4
    assert r["glyph_rows_by_pattern"]["55aa55aa55aa55aa"] == [3]


def test_ega_display_equals_buffer():
    assert s.ega_display_matches_buffer()["mismatched_agi_pixels"] == 0


def test_heap_top_wraps_to_0x10():
    r = s.heap_base_and_top_wrap()
    assert (r["heap_at_load"]["base"], r["heap_at_load"]["top"]) == ("0x1e80", "0x10")
    assert r["exact_fit"]["heap_after"]["next"] == "0x10"


def test_speaker_divisor_is_twelve_times_the_tone():
    r = s.speaker_divisor_on_pc()
    assert r["pit_divisors"] == r["note_divisors_x12"]
