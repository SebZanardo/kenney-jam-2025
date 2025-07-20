from components.camera import camera_to_screen_shake
import core.constants as c
import core.globals as g


def hud_render():
    for x in range(c.WINDOW_WIDTH // 14):
        g.window.blit(g.TERRAIN[7], (x * 14 - 2, -1))
        g.window.blit(g.TERRAIN[3], (x * 14 - 2, 3))
        g.window.blit(g.TERRAIN[7], (x * 14 - 2, c.WINDOW_HEIGHT - c.TILE_SIZE))
        g.window.blit(g.TERRAIN[2], (x * 14 - 2, c.WINDOW_HEIGHT - c.TILE_SIZE - 4))

    for y in range(c.GRID_HEIGHT_TILES):
        g.window.blit(
            g.TERRAIN[5],
            camera_to_screen_shake(g.camera, -1 * c.TILE_SIZE, y * c.TILE_SIZE),
        )
        g.window.blit(
            g.TERRAIN[6],
            camera_to_screen_shake(g.camera, -2 * c.TILE_SIZE, y * c.TILE_SIZE),
        )
        g.window.blit(
            g.TERRAIN[4],
            camera_to_screen_shake(g.camera, c.GRID_WIDTH, y * c.TILE_SIZE),
        )
        g.window.blit(
            g.TERRAIN[6],
            camera_to_screen_shake(g.camera, c.GRID_WIDTH + c.TILE_SIZE, y * c.TILE_SIZE),
        )
