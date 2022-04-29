def composite_cel(screen, loop_idx, cel):
    x, y, end = 0, 0, cel.height
    mirrored = cel.mirror and loop_idx != cel.non_mirror_idx
    pixels = cel.cel_data

    for color, num_pixels in pixels:
        if y >= end:
            break
        if color == 0 == num_pixels:
            # we've finished a line, so reset x to the beginning and move y down
            x, y = 0, y + 1
            continue

        n = x + num_pixels

        for x0 in range(x, n):
            if color != cel.alpha:
                screen.store(cel.width - 1 - x0 if mirrored else x0, y, color)

        # because we drew all the way to n, we need to set x to n here
        x = n
