"""Tests from the audited rules in andromeda-wiki/concepts/picture-rendering.md."""
from rules_model import BLANK, H, W, render, splatter_step

TWO_COLUMNS = 0xA000  # columns 0 and 1 of a 2-wide circle mask
PENS = [[0x8000], [TWO_COLUMNS] * 3] + [[0] * (2 * size + 1) for size in range(2, 8)]
BLACK = [0xF0, 0x00]


def draw(*stream):
    return render(bytes(stream) + b"\xff", PENS)


def pixel(buf, x, y):
    return buf[y * W + x]


def changed(buf):
    return {(i % W, i // W) for i, value in enumerate(buf) if value != BLANK}


def test_empty_picture_is_white_at_priority_4():
    assert draw() == bytes([BLANK]) * (W * H)


def test_color_writes_the_low_nibble_only():
    assert pixel(draw(*BLACK, 0xF6, 5, 5), 5, 5) == 0x40


def test_nothing_is_drawn_until_a_layer_is_enabled():
    assert not changed(draw(0xF6, 5, 5, 20, 5))


def test_coordinates_clamp_to_the_screen():
    assert changed(draw(*BLACK, 0xF6, 200, 200)) == {(159, 167)}


def test_reserved_opcodes_and_their_bytes_are_skipped():
    assert changed(draw(*BLACK, 0xFB, 1, 2, 3, 0xF6, 9, 9)) == {(9, 9)}


def test_straight_line_includes_both_ends():
    assert changed(draw(*BLACK, 0xF6, 2, 3, 5, 3)) == {(2, 3), (3, 3), (4, 3), (5, 3)}


def test_diagonal_line_reaches_its_endpoint_when_sum_is_small():
    assert (30, 20) in changed(draw(*BLACK, 0xF6, 0, 0, 30, 20))


def test_long_diagonal_overflows_and_misses_its_endpoint():
    stream = bytes([*BLACK, 0xF6, 0, 0, 159, 167, 0xFF])
    assert pixel(render(stream, PENS), 159, 167) == BLANK
    assert pixel(render(stream, PENS, wrap_line=False), 159, 167) == 0x40


def test_pen_size_0_is_one_pixel():
    assert changed(draw(*BLACK, 0xF9, 0, 0xFA, 80, 80)) == {(80, 80)}


def test_pen_size_1_circle_is_a_two_by_three_block():
    expected = {(x, y) for x in (79, 80) for y in (79, 80, 81)}
    assert changed(draw(*BLACK, 0xF9, 1, 0xFA, 80, 80)) == expected


def test_rectangle_pen_is_size_plus_1_wide_and_2_size_plus_1_tall():
    assert len(changed(draw(*BLACK, 0xF9, 0x12, 0xFA, 80, 80))) == 3 * 5


def test_filling_white_does_nothing_even_with_priority_enabled():
    assert not changed(draw(0xF0, 0x0F, 0xF2, 5, 0xF8, 10, 10))


def test_filling_priority_4_alone_does_nothing():
    assert not changed(draw(0xF1, 0xF2, 4, 0xF8, 10, 10))


def test_both_layer_fill_writes_priority_at_every_filled_pixel():
    assert pixel(draw(0xF0, 1, 0xF2, 7, 0xF8, 10, 10), 100, 100) == 0x71


def test_fill_is_4_connected_so_a_diagonal_wall_holds():
    buf = draw(*BLACK, 0xF6, 0, 10, 10, 0, 0xF0, 1, 0xF8, 0, 0)
    assert pixel(buf, 0, 0) == 0x41
    assert pixel(buf, 20, 20) == BLANK


def test_splatter_ignores_the_textures_low_bit():
    def plot(texture):
        return draw(*BLACK, 0xF9, 0x22, 0xFA, texture, 80, 80)

    assert plot(2) == plot(3)


def test_splatter_register_has_period_255():
    register, steps = 1, 0
    while True:
        register, _ = splatter_step(register)
        steps += 1
        if register == 1:
            break
    assert steps == 255
