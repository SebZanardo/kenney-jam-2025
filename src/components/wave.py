from dataclasses import dataclass

import components.enemy as e


@dataclass(frozen=True)
class Wave:
    enemy_type: e.EnemyType
    count: int
    # This is float because if < 1 then can spawn multiple per tick
    spawn_tick: float


@dataclass
class WaveData:
    number: int = 0

    # For wave we are on
    spawn_enemy_type: e.EnemyType = e.EnemyType.GROUND
    spawn_remaining: int = 0
    spawn_tick: float = 0
    spawn_tick_counter: float = 0
    spawn_instruction_index: int = -1
    spawn_done = False


# This stores all wave data
waves: list[list[Wave]] = [
    [Wave(e.EnemyType.GROUND, 1, 10)],
    [Wave(e.EnemyType.GROUND, 3, 20)],
    [Wave(e.EnemyType.GROUND, 5, 15)],
    [Wave(e.EnemyType.GROUND_HEAVY, 1, 10)],
    [Wave(e.EnemyType.GROUND, 10, 8)],
    [Wave(e.EnemyType.GROUND_HEAVY, 3, 45)],
    [Wave(e.EnemyType.GROUND_HEAVY, 1, 10), Wave(e.EnemyType.GROUND, 1, 20)] * 3,
    [Wave(e.EnemyType.GROUND, 15, 15)],
    [Wave(e.EnemyType.GROUND_HEAVY, 5, 30)],
    [Wave(e.EnemyType.GROUND, 3, 25), Wave(e.EnemyType.GROUND_HEAVY, 1, 10)] * 3,
    [Wave(e.EnemyType.GROUND_FAST, 3, 120)],
    [Wave(e.EnemyType.GROUND_HEAVY, 10, 45)],
    [Wave(e.EnemyType.GROUND_HEAVY, 1, 10), Wave(e.EnemyType.GROUND_FAST, 1, 60)] * 5,
    [Wave(e.EnemyType.GROUND, 20, 8)],
    [Wave(e.EnemyType.GROUND_FAST, 10, 30)],
    [Wave(e.EnemyType.FLYING_FAST, 3, 120)],
    [Wave(e.EnemyType.GROUND_HEAVY, 20, 30)],
    [Wave(e.EnemyType.GROUND, 20, 8)],
    [Wave(e.EnemyType.FLYING_FAST, 8, 60)],
    [Wave(e.EnemyType.GROUND_HEAVY, 30, 60)],
    [Wave(e.EnemyType.FLYING, 5, 120)],
    [Wave(e.EnemyType.FLYING_FAST, 10, 60)],
    [Wave(e.EnemyType.FLYING, 2, 30), Wave(e.EnemyType.FLYING_FAST, 1, 10)] * 3,
    [Wave(e.EnemyType.GROUND, 40, 10)],
    [Wave(e.EnemyType.GROUND_HEAVY, 40, 30)],
    [Wave(e.EnemyType.GROUND_FAST, 40, 20)],
    [Wave(e.EnemyType.GROUND_HEAVY_FAST, 3, 120)],
    [Wave(e.EnemyType.FLYING, 20, 30)],
    [Wave(e.EnemyType.GROUND_HEAVY, 20, 50)],
    [Wave(e.EnemyType.FLYING_FAST, 20, 20)],
    [Wave(e.EnemyType.FLYING_HEAVY, 1, 20)],
    [Wave(e.EnemyType.GROUND_HEAVY, 10, 30)],
    [Wave(e.EnemyType.GROUND_FAST, 10, 50)],
    [Wave(e.EnemyType.GROUND, 50, 10)],
    [Wave(e.EnemyType.FLYING, 2, 30), Wave(e.EnemyType.FLYING_FAST, 3, 20)] * 5,
    [Wave(e.EnemyType.FLYING_HEAVY, 3, 200)],
    [Wave(e.EnemyType.GROUND_HEAVY_FAST, 10, 40), Wave(e.EnemyType.GROUND_FAST, 5, 20)] * 5,
    [Wave(e.EnemyType.GROUND, 30, 10)],
    [Wave(e.EnemyType.FLYING_HEAVY, 5, 200)],
    [Wave(e.EnemyType.GROUND, 5, 10), Wave(e.EnemyType.GROUND_HEAVY, 5, 30)] * 3,
    [Wave(e.EnemyType.GROUND_FAST, 50, 20)],
    [Wave(e.EnemyType.FLYING_FAST, 20, 50)],
    [Wave(e.EnemyType.GROUND_HEAVY_FAST, 20, 30)],
    [Wave(e.EnemyType.FLYING, 20, 30)],
    [Wave(e.EnemyType.GROUND_HEAVY, 50, 30)],
    [Wave(e.EnemyType.GROUND_SUPER_HEAVY, 1, 100)],
    [Wave(e.EnemyType.FLYING_HEAVY, 10, 60)],
    [Wave(e.EnemyType.GROUND_SUPER_HEAVY, 3, 120)],
    [Wave(e.EnemyType.GROUND_FAST, 10, 10), Wave(e.EnemyType.FLYING_FAST, 10, 10)] * 3,
    [Wave(e.EnemyType.GROUND_HEAVY_FAST, 20, 20), Wave(e.EnemyType.FLYING_HEAVY, 20, 30)] * 3,
    [Wave(e.EnemyType.GROUND_SUPER_HEAVY, 10, 30)],
]

WAVE_COUNT = len(waves)
wave_data = WaveData()


def wave_reset() -> None:
    e.active_enemies = 0

    wave_data.number = 0

    # For wave we are on
    wave_data.spawn_enemy_type = e.EnemyType.GROUND
    wave_data.spawn_remaining = 0
    wave_data.spawn_tick = 0
    wave_data.spawn_tick_counter = 0
    wave_data.spawn_instruction_index = -1
    wave_data.spawn_done = False


def wave_update() -> None:
    if wave_data.spawn_done:
        # If wave has finished spawning and all enemies died, spawn next wave
        if e.active_enemies == 0:
            wave_new()
            return
    else:
        # Continue spawning current wave
        while wave_data.spawn_tick_counter >= wave_data.spawn_tick:
            # If we spawned all the enemies, increment to next instruction
            if wave_data.spawn_remaining <= 0:
                wave_data.spawn_instruction_index += 1
                wave_instruction_new()
                if wave_data.spawn_done:
                    break

            e.enemy_spawn(wave_data.spawn_enemy_type)
            # decrement the remaining count regardless of whether it succeeded or not
            # to avoid getting stuck in an infinite loop!
            wave_data.spawn_remaining -= 1
            wave_data.spawn_tick_counter -= wave_data.spawn_tick

        wave_data.spawn_tick_counter += 1

    # Update all enemies
    i = 0
    while i < e.active_enemies:
        died = e.enemy_update(i)
        if died:
            e.enemy_remove(i)
        else:
            i += 1


def wave_new() -> None:
    wave_data.number += 1
    print(f"New wave: {wave_data.number}")

    # Increase enemy health multiplier
    e.enemy_health_multiplier = 1 + (wave_data.number / WAVE_COUNT) * 20

    wave_data.spawn_instruction_index = 0
    wave_data.spawn_done = False
    wave_instruction_new()


def wave_instruction_new() -> None:
    w = waves[wave_data.number % WAVE_COUNT]

    if wave_data.spawn_instruction_index >= len(w):
        # Signal that spawn wave is done
        wave_data.spawn_done = True
        print("Current wave spawning complete")
        return

    wave_instruction: Wave = w[wave_data.spawn_instruction_index]

    wave_data.spawn_enemy_type = wave_instruction.enemy_type
    wave_data.spawn_remaining = wave_instruction.count
    wave_data.spawn_tick = wave_instruction.spawn_tick
    wave_data.spawn_tick_counter = 0

    print(f"New wave spawn index: {wave_data.spawn_instruction_index}")
