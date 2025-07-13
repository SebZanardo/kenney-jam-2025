import asyncio
import pygame

import core.constants as c
import core.input as i
from core.setup import window, clock

from components.statemachine import StateMachine, statemachine_initialise, statemachine_execute
from scenes.manager import SCENE_MAPPING, SceneState


pygame.init()


async def main() -> None:
    scene_manager = StateMachine()
    statemachine_initialise(scene_manager, SCENE_MAPPING, SceneState.MENU)

    # Should these be global too with clock?
    mouse_buffer: i.InputBuffer = [i.InputState.NOTHING for _ in i.MouseButton]
    action_buffer: i.InputBuffer = [i.InputState.NOTHING for _ in i.Action]
    last_pressed = [i.action_mappings[action][0] for action in i.Action]

    print("Starting game loop")

    while True:
        elapsed_time = clock.tick(c.FPS)
        dt = elapsed_time / 1000.0  # Convert to seconds
        dt = min(dt, c.MAX_DT)  # Clamp delta time
        # dt *= g.time_dilation

        i.update_action_buffer(action_buffer, last_pressed)

        running = i.input_event_queue(action_buffer)

        if not running:
            terminate()

        i.update_mouse_buffer(mouse_buffer)

        statemachine_execute(scene_manager, dt, action_buffer, mouse_buffer)

        # Keep these calls together in this order
        pygame.display.flip()
        await asyncio.sleep(0)  # Very important, and keep it 0


def terminate() -> None:
    print("Terminated application")

    pygame.mixer.stop()
    window.fill(c.BLACK)

    pygame.quit()
    raise SystemExit


if __name__ == "__main__":
    asyncio.run(main())
