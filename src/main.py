import asyncio
import pygame

import core.constants as c
import core.input as t
import core.globals as g

from core.setup import setup

from components.statemachine import statemachine_execute
from components.audio import play_music


async def main() -> None:
    setup()
    print("Starting game loop")

    play_music(g.GAME_MUSIC, -1)

    while True:
        g.clock.tick(c.FPS)
        # elapsed_time = g.clock.tick(c.FPS)
        # g.dt = elapsed_time / 1000.0  # Convert to seconds
        # g.dt = min(g.dt, c.MAX_DT)  # Clamp delta time
        # dt *= g.time_dilation

        g.last_mouse_pos = g.mouse_pos[:]
        g.mouse_pos = pygame.mouse.get_pos()
        t.update_action_buffer()

        running = t.input_event_queue()

        if not running:
            terminate()

        t.update_mouse_buffer()

        statemachine_execute(g.scene_manager)

        # Keep these calls together in this order
        pygame.display.flip()
        await asyncio.sleep(0)  # Very important, and keep it 0


def terminate() -> None:
    print("Terminated application")

    pygame.mixer.stop()
    g.window.fill(c.BLACK)

    pygame.quit()
    raise SystemExit


if __name__ == "__main__":
    asyncio.run(main())
