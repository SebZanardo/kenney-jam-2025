import platform
import asyncio
import pygame

import core.constants as c
import core.assets as a


pygame.init()

if c.IS_WEB:
    platform.window.canvas.style.imageRendering = "pixelated"
    window = pygame.display.set_mode(c.WINDOW_SETUP["size"])
else:
    window = pygame.display.set_mode(**c.WINDOW_SETUP)

pygame.display.set_caption(c.CAPTION)
pygame.display.set_icon(a.ICON)

clock = pygame.time.Clock()


async def main() -> None:
    while True:
        clock.tick(c.FPS)

        # INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                return

            # HACK: For quick development
            # NOTE: It overrides exitting fullscreen when in browser
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
                return

        # UPDATE

        # RENDER
        window.fill(c.WHITE)

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
