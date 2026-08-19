#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAJD AI GAME FACTORY
MAJD-AI-MASTERMIND-01.py

العقل المدبر للتطور المستمر
=====================================================

المكونات:
- بيئة لعبة شبكية مع فيزياء بسيطة
- وكيل شبكة عصبية صغيرة (MLP) قابلة للتطور
- فرد (Individual) = مستوى + أوزان الشبكة
- خوارزمية جينية
- عقل مدبر (Mastermind)
- ضبط تلقائي لمعدلات الطفرة
- حفظ واستعادة حالة التطور
- تشغيل دورة التطور تلقائيًا
"""

import numpy as np
import random
import os
import time
import pickle
from typing import List, Tuple, Optional


# ============================================================
# GENERAL CONFIGURATION
# ============================================================

LEVEL_WIDTH = 16
LEVEL_HEIGHT = 16

POPULATION_SIZE = 30
NUM_GENERATIONS = 1000

MAX_STEPS = 200


# ============================================================
# NEURAL NETWORK CONFIGURATION
# ============================================================

OBS_DIM = 10
HIDDEN_DIM = 8
ACTION_DIM = 4


# ============================================================
# EVOLUTION CONFIGURATION
# ============================================================

INIT_MUTATION_RATE = 0.1
INIT_WEIGHT_MUTATION_RATE = 0.2

MUTATION_STEP = 0.01
STAGNATION_THRESHOLD = 10


# ============================================================
# LEVEL CELL TYPES
# ============================================================

EMPTY = 0
PLATFORM = 1
OBSTACLE = 2
GOAL = 3
START = 4


# ============================================================
# LEVEL UTILITIES
# ============================================================

def create_empty_level(
    width: int = LEVEL_WIDTH,
    height: int = LEVEL_HEIGHT
) -> np.ndarray:

    return np.zeros(
        (height, width),
        dtype=np.uint8
    )


def add_ground(
    level: np.ndarray,
    ground_height: int = 2
) -> None:

    level[-ground_height:, :] = PLATFORM


def find_cell(
    level: np.ndarray,
    value: int
) -> Optional[Tuple[int, int]]:

    indices = np.argwhere(level == value)

    if len(indices) > 0:
        return tuple(indices[0])

    return None


def save_level_image(
    level: np.ndarray,
    path: str
) -> None:

    try:

        from PIL import Image

        color_map = {
            EMPTY: (255, 255, 255),
            PLATFORM: (139, 69, 19),
            OBSTACLE: (255, 0, 0),
            GOAL: (0, 255, 0),
            START: (0, 0, 255)
        }

        height, width = level.shape

        img = np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )

        for y in range(height):
            for x in range(width):

                img[y, x] = color_map.get(
                    level[y, x],
                    (0, 0, 0)
                )

        Image.fromarray(img).save(path)

    except ImportError:

        pass


# ============================================================
# RANDOM LEVEL GENERATOR
# ============================================================

def generate_random_level() -> np.ndarray:

    level = create_empty_level()

    add_ground(
        level,
        ground_height=2
    )

    ground_y = LEVEL_HEIGHT - 1
    start_y = LEVEL_HEIGHT - 3

    start_x = random.randint(
        0,
        2
    )

    level[
        start_y,
        start_x
    ] = START

    end_x = random.randint(
        LEVEL_WIDTH - 3,
        LEVEL_WIDTH - 1
    )

    level[
        start_y,
        end_x
    ] = GOAL


    # --------------------------------------------------------
    # FLOATING PLATFORMS
    # --------------------------------------------------------

    num_platforms = random.randint(
        3,
        8
    )

    for _ in range(num_platforms):

        plat_x = random.randint(
            0,
            LEVEL_WIDTH - 4
        )

        plat_y = random.randint(
            3,
            LEVEL_HEIGHT - 5
        )

        plat_len = random.randint(
            2,
            5
        )

        if (
            plat_y == start_y
            and (
                start_x in range(
                    plat_x,
                    plat_x + plat_len
                )
                or
                end_x in range(
                    plat_x,
                    plat_x + plat_len
                )
            )
        ):
            continue

        level[
            plat_y,
            plat_x:plat_x + plat_len
        ] = PLATFORM


    # --------------------------------------------------------
    # OBSTACLES
    # --------------------------------------------------------

    num_obstacles = random.randint(
        2,
        5
    )

    for _ in range(num_obstacles):

        obs_x = random.randint(
            0,
            LEVEL_WIDTH - 1
        )

        if (
            obs_x == start_x
            or
            obs_x == end_x
        ):
            continue

        if level[
            ground_y,
            obs_x
        ] == EMPTY:

            level[
                ground_y,
                obs_x
            ] = OBSTACLE

    return level


# ============================================================
# GAME ENVIRONMENT
# ============================================================

class GameEnvironment:

    def __init__(
        self,
        level: np.ndarray,
        max_steps: int = MAX_STEPS
    ):

        self.level = level.copy()

        self.height, self.width = level.shape

        self.max_steps = max_steps

        self.reset()


    def reset(self):

        start_pos = find_cell(
            self.level,
            START
        )

        if start_pos is None:

            self.player_y = 0
            self.player_x = 0

        else:

            self.player_y, self.player_x = start_pos

        self.velocity_y = 0

        self.on_ground = False

        self.done = False

        self.won = False

        self.steps = 0


    def get_observation(self) -> np.ndarray:

        obs = np.zeros(
            OBS_DIM,
            dtype=np.float32
        )

        obs[0] = self.player_x / self.width

        obs[1] = self.player_y / self.height

        obs[2] = self.velocity_y / 3.0

        obs[3] = (
            1.0
            if self.on_ground
            else 0.0
        )

        goal_pos = find_cell(
            self.level,
            GOAL
        )

        if goal_pos:

            obs[4] = (
                goal_pos[1] - self.player_x
            ) / self.width

            obs[5] = (
                goal_pos[0] - self.player_y
            ) / self.height

        else:

            obs[4] = 0.0
            obs[5] = 0.0


        directions = [
            (-1, 0),
            (1, 0),
            (0, 1),
            (0, -1)
        ]

        for i, (dy, dx) in enumerate(
            directions
        ):

            ny = self.player_y + dy
            nx = self.player_x + dx

            if (
                0 <= ny < self.height
                and
                0 <= nx < self.width
            ):

                cell = self.level[
                    ny,
                    nx
                ]

                if cell == PLATFORM:

                    obs[6 + i] = 1.0

                elif cell == OBSTACLE:

                    obs[6 + i] = -1.0

                elif cell == GOAL:

                    obs[6 + i] = 0.5

        return obs


    def is_solid(
        self,
        x: int,
        y: int
    ) -> bool:

        if (
            0 <= y < self.height
            and
            0 <= x < self.width
        ):

            return (
                self.level[y, x]
                == PLATFORM
            )

        if y >= self.height:

            return True

        return False


    def is_obstacle(
        self,
        x: int,
        y: int
    ) -> bool:

        if (
            0 <= y < self.height
            and
            0 <= x < self.width
        ):

            return (
                self.level[y, x]
                == OBSTACLE
            )

        return False


    def is_goal(
        self,
        x: int,
        y: int
    ) -> bool:

        if (
            0 <= y < self.height
            and
            0 <= x < self.width
        ):

            return (
                self.level[y, x]
                == GOAL
            )

        return False


    def step(
        self,
        action: int
    ) -> Tuple[np.ndarray, float, bool]:

        if self.done:

            return (
                self.get_observation(),
                0.0,
                True
            )


        # ----------------------------------------------------
        # HORIZONTAL MOVEMENT
        # ----------------------------------------------------

        if action == 1:

            dx = -1

        elif action == 2:

            dx = 1

        else:

            dx = 0


        # ----------------------------------------------------
        # JUMP
        # ----------------------------------------------------

        if (
            action == 3
            and
            self.on_ground
        ):

            self.velocity_y = -2.0


        # ----------------------------------------------------
        # GRAVITY
        # ----------------------------------------------------

        self.velocity_y += 0.5

        self.velocity_y = min(
            self.velocity_y,
            2.0
        )


        new_x = (
            self.player_x
            + dx
        )

        new_y = (
            self.player_y
            + int(
                round(
                    self.velocity_y
                )
            )
        )


        # ----------------------------------------------------
        # OBSTACLE COLLISION
        # ----------------------------------------------------

        if (
            self.is_obstacle(
                new_x,
                new_y
            )
            or
            self.is_obstacle(
                new_x,
                self.player_y
            )
        ):

            self.done = True
            self.won = False
            self.steps += 1

            return (
                self.get_observation(),
                -10.0,
                True
            )


        # ----------------------------------------------------
        # GOAL
        # ----------------------------------------------------

        if self.is_goal(
            new_x,
            new_y
        ):

            self.player_x = new_x
            self.player_y = new_y

            self.done = True
            self.won = True

            self.steps += 1

            return (
                self.get_observation(),
                100.0,
                True
            )


        # ----------------------------------------------------
        # PLATFORM COLLISION
        # ----------------------------------------------------

        if self.is_solid(
            new_x,
            new_y
        ):

            if self.velocity_y > 0:

                new_y = self.player_y

                self.velocity_y = 0

                self.on_ground = True

            elif self.velocity_y < 0:

                new_y = self.player_y

                self.velocity_y = 0

            else:

                new_x = self.player_x

        else:

            self.player_x = new_x
            self.player_y = new_y

            if self.is_solid(
                self.player_x,
                self.player_y + 1
            ):

                self.on_ground = True

                self.velocity_y = 0

            else:

                self.on_ground = False


        # ----------------------------------------------------
        # FALL OUTSIDE MAP
        # ----------------------------------------------------

        if self.player_y >= self.height:

            self.done = True
            self.won = False

            self.steps += 1

            return (
                self.get_observation(),
                -10.0,
                True
            )


        self.steps += 1


        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        if self.steps >= self.max_steps:

            self.done = True
            self.won = False

            return (
                self.get_observation(),
                -1.0,
                True
            )


        reward = -0.1

        return (
            self.get_observation(),
            reward,
            False
        )


# ============================================================
# NEURAL AI AGENT
# ============================================================

class NeuralAgent:

    def __init__(
        self,
        input_dim: int = OBS_DIM,
        hidden_dim: int = HIDDEN_DIM,
        output_dim: int = ACTION_DIM
    ):

        self.input_dim = input_dim

        self.hidden_dim = hidden_dim

        self.output_dim = output_dim

        self.weights = self._init_weights()


    def _init_weights(
        self
    ) -> List[np.ndarray]:

        W1 = (
            np.random.randn(
                self.input_dim,
                self.hidden_dim
            )
            * 0.5
        )

        b1 = np.zeros(
            self.hidden_dim
        )

        W2 = (
            np.random.randn(
                self.hidden_dim,
                self.output_dim
            )
            * 0.5
        )

        b2 = np.zeros(
            self.output_dim
        )

        return [
            W1,
            b1,
            W2,
            b2
        ]


    def forward(
        self,
        obs: np.ndarray
    ) -> np.ndarray:

        W1, b1, W2, b2 = self.weights

        z1 = (
            np.dot(
                obs,
                W1
            )
            + b1
        )

        a1 = np.tanh(
            z1
        )

        z2 = (
            np.dot(
                a1,
                W2
            )
            + b2
        )

        return z2


    def get_action(
        self,
        obs: np.ndarray,
        epsilon: float = 0.0
    ) -> int:

        if random.random() < epsilon:

            return random.randint(
                0,
                self.output_dim - 1
            )

        q_values = self.forward(
            obs
        )

        return int(
            np.argmax(
                q_values
            )
        )


    def get_weights_flat(
        self
    ) -> np.ndarray:

        return np.concatenate(
            [
                w.flatten()
                for w in self.weights
            ]
        )


    def set_weights_from_flat(
        self,
        flat: np.ndarray
    ) -> None:

        idx = 0

        new_weights = []

        for w in self.weights:

            size = w.size

            new_weights.append(
                flat[
                    idx:idx + size
                ].reshape(
                    w.shape
                )
            )

            idx += size

        self.weights = new_weights


# ============================================================
# EVOLUTION INDIVIDUAL
# ============================================================

class Individual:

    def __init__(
        self,
        level: np.ndarray,
        agent_weights_flat: np.ndarray
    ):

        self.level = level

        self.agent_weights_flat = (
            agent_weights_flat
        )

        self.fitness = -float(
            "inf"
        )


    def evaluate(
        self,
        env_class: type = GameEnvironment,
        max_steps: int = MAX_STEPS,
        epsilon: float = 0.0
    ) -> float:

        env = env_class(
            self.level,
            max_steps
        )

        agent = NeuralAgent(
            OBS_DIM,
            HIDDEN_DIM,
            ACTION_DIM
        )

        agent.set_weights_from_flat(
            self.agent_weights_flat
        )

        total_reward = 0.0

        done = False

        while not done:

            obs = env.get_observation()

            action = agent.get_action(
                obs,
                epsilon
            )

            _, reward, done = env.step(
                action
            )

            total_reward += reward


        if env.won:

            total_reward += (
                50.0
                -
                env.steps * 0.5
            )

        else:

            total_reward -= 20.0


        self.fitness = total_reward

        return total_reward


    def clone(
        self
    ) -> "Individual":

        clone = Individual(
            self.level.copy(),
            self.agent_weights_flat.copy()
        )

        clone.fitness = self.fitness

        return clone


# ============================================================
# GENETIC CROSSOVER
# ============================================================

def crossover(
    parent1: Individual,
    parent2: Individual
) -> Individual:

    cut = random.randint(
        1,
        LEVEL_HEIGHT - 1
    )

    child_level = np.zeros_like(
        parent1.level
    )

    child_level[
        :cut,
        :
    ] = parent1.level[
        :cut,
        :
    ]

    child_level[
        cut:,
        :
    ] = parent2.level[
        cut:,
        :
    ]


    cut_w = random.randint(
        1,
        len(
            parent1.agent_weights_flat
        ) - 1
    )

    child_weights = np.concatenate(
        [
            parent1.agent_weights_flat[
                :cut_w
            ],

            parent2.agent_weights_flat[
                cut_w:
            ]
        ]
    )

    return Individual(
        child_level,
        child_weights
    )


# ============================================================
# MUTATION
# ============================================================

def mutate(
    individual: Individual,
    level_mutation_rate: float,
    weight_mutation_rate: float
) -> Individual:

    mutated_level = (
        individual.level.copy()
    )


    for y in range(
        LEVEL_HEIGHT
    ):

        for x in range(
            LEVEL_WIDTH
        ):

            if (
                random.random()
                <
                level_mutation_rate
            ):

                new_val = random.choices(
                    [
                        EMPTY,
                        PLATFORM,
                        OBSTACLE,
                        GOAL,
                        START
                    ],
                    weights=[
                        0.6,
                        0.3,
                        0.05,
                        0.025,
                        0.025
                    ]
                )[0]

                mutated_level[
                    y,
                    x
                ] = new_val


    if find_cell(
        mutated_level,
        START
    ) is None:

        mutated_level[
            LEVEL_HEIGHT - 3,
            0
        ] = START


    if find_cell(
        mutated_level,
        GOAL
    ) is None:

        mutated_level[
            LEVEL_HEIGHT - 3,
            LEVEL_WIDTH - 1
        ] = GOAL


    mutated_weights = (
        individual
        .agent_weights_flat
        .copy()
    )


    noise = (
        np.random.randn(
            len(
                mutated_weights
            )
        )
        *
        weight_mutation_rate
    )


    mutated_weights += noise


    return Individual(
        mutated_level,
        mutated_weights
    )


# ============================================================
# TOURNAMENT SELECTION
# ============================================================

def tournament_selection(
    population: List[Individual],
    k: int = 3
) -> Individual:

    selected = random.sample(
        population,
        min(
            k,
            len(population)
        )
    )

    return max(
        selected,
        key=lambda ind: ind.fitness
    )


# ============================================================
# MAJD AI MASTERMIND
# ============================================================

class Mastermind:

    def __init__(
        self,
        population_size: int = POPULATION_SIZE,
        level_width: int = LEVEL_WIDTH,
        level_height: int = LEVEL_HEIGHT,
        max_steps: int = MAX_STEPS,
        num_generations: int = NUM_GENERATIONS,
        save_dir: str = "evolution_output",
        resume: bool = False
    ):

        self.population_size = (
            population_size
        )

        self.level_width = (
            level_width
        )

        self.level_height = (
            level_height
        )

        self.max_steps = (
            max_steps
        )

        self.num_generations = (
            num_generations
        )

        self.save_dir = save_dir

        os.makedirs(
            save_dir,
            exist_ok=True
        )


        self.population: List[
            Individual
        ] = []


        self.best_individual: Optional[
            Individual
        ] = None


        self.best_fitness_history: List[
            float
        ] = []


        self.avg_fitness_history: List[
            float
        ] = []


        self.level_mutation_rate = (
            INIT_MUTATION_RATE
        )

        self.weight_mutation_rate = (
            INIT_WEIGHT_MUTATION_RATE
        )

        self.stagnation_counter = 0

        self.last_best_fitness = -float(
            "inf"
        )


        if resume:

            self._load_state()


    # ========================================================
    # INITIALIZE POPULATION
    # ========================================================

    def _initialize_population(
        self
    ):

        self.population = []

        for _ in range(
            self.population_size
        ):

            level = (
                generate_random_level()
            )

            agent = NeuralAgent(
                OBS_DIM,
                HIDDEN_DIM,
                ACTION_DIM
            )

            weights_flat = (
                agent.get_weights_flat()
            )

            self.population.append(
                Individual(
                    level,
                    weights_flat
                )
            )


    # ========================================================
    # EVALUATE POPULATION
    # ========================================================

    def _evaluate_population(
        self,
        epsilon: float = 0.0
    ):

        fitnesses = []

        for ind in self.population:

            fit = ind.evaluate(
                epsilon=epsilon
            )

            fitnesses.append(
                fit
            )


        self.avg_fitness_history.append(
            float(
                np.mean(
                    fitnesses
                )
            )
        )


        best_idx = int(
            np.argmax(
                fitnesses
            )
        )


        if (
            self.best_individual is None
            or
            fitnesses[best_idx]
            >
            self.best_individual.fitness
        ):

            self.best_individual = (
                self.population[
                    best_idx
                ].clone()
            )


        self.best_fitness_history.append(
            self.best_individual.fitness
        )


    # ========================================================
    # EVOLVE
    # ========================================================

    def _evolve(
        self
    ):

        new_population = []


        elite_count = max(
            1,
            int(
                self.population_size
                * 0.1
            )
        )


        sorted_pop = sorted(
            self.population,
            key=lambda ind: ind.fitness,
            reverse=True
        )


        new_population.extend(
            [
                ind.clone()
                for ind
                in sorted_pop[
                    :elite_count
                ]
            ]
        )


        while (
            len(new_population)
            <
            self.population_size
        ):

            parent1 = tournament_selection(
                self.population
            )

            parent2 = tournament_selection(
                self.population
            )


            child = crossover(
                parent1,
                parent2
            )


            child = mutate(
                child,
                self.level_mutation_rate,
                self.weight_mutation_rate
            )


            new_population.append(
                child
            )


        self.population = (
            new_population
        )


    # ========================================================
    # SELF ADJUST MUTATION RATES
    # ========================================================

    def _adjust_mutation_rates(
        self
    ):

        if (
            self.best_fitness_history[-1]
            >
            self.last_best_fitness
            + 1e-6
        ):

            self.stagnation_counter = 0


            self.level_mutation_rate = max(
                0.01,
                self.level_mutation_rate
                -
                MUTATION_STEP
            )


            self.weight_mutation_rate = max(
                0.05,
                self.weight_mutation_rate
                -
                MUTATION_STEP
            )


        else:

            self.stagnation_counter += 1


            if (
                self.stagnation_counter
                >=
                STAGNATION_THRESHOLD
            ):

                self.level_mutation_rate = min(
                    0.5,
                    self.level_mutation_rate
                    +
                    MUTATION_STEP * 2
                )


                self.weight_mutation_rate = min(
                    0.8,
                    self.weight_mutation_rate
                    +
                    MUTATION_STEP * 2
                )


                self.stagnation_counter = 0


        self.last_best_fitness = (
            self.best_fitness_history[-1]
        )


    # ========================================================
    # SAVE STATE
    # ========================================================

    def _save_state(
        self
    ):

        if self.best_individual:

            save_path = os.path.join(
                self.save_dir,
                "best_individual.pkl"
            )


            with open(
                save_path,
                "wb"
            ) as f:

                pickle.dump(
                    self.best_individual,
                    f
                )


            save_level_image(
                self.best_individual.level,
                os.path.join(
                    self.save_dir,
                    "best_level.png"
                )
            )


        state = {

            "population":
                self.population,

            "best_individual":
                self.best_individual,

            "best_fitness_history":
                self.best_fitness_history,

            "avg_fitness_history":
                self.avg_fitness_history,

            "level_mutation_rate":
                self.level_mutation_rate,

            "weight_mutation_rate":
                self.weight_mutation_rate,

            "stagnation_counter":
                self.stagnation_counter,

            "last_best_fitness":
                self.last_best_fitness
        }


        with open(
            os.path.join(
                self.save_dir,
                "evolution_state.pkl"
            ),
            "wb"
        ) as f:

            pickle.dump(
                state,
                f
            )


    # ========================================================
    # LOAD STATE
    # ========================================================

    def _load_state(
        self
    ):

        state_path = os.path.join(
            self.save_dir,
            "evolution_state.pkl"
        )


        if os.path.exists(
            state_path
        ):

            with open(
                state_path,
                "rb"
            ) as f:

                state = pickle.load(
                    f
                )


            self.population = state.get(
                "population",
                []
            )


            self.best_individual = state.get(
                "best_individual"
            )


            self.best_fitness_history = state.get(
                "best_fitness_history",
                []
            )


            self.avg_fitness_history = state.get(
                "avg_fitness_history",
                []
            )


            self.level_mutation_rate = state.get(
                "level_mutation_rate",
                INIT_MUTATION_RATE
            )


            self.weight_mutation_rate = state.get(
                "weight_mutation_rate",
                INIT_WEIGHT_MUTATION_RATE
            )


            self.stagnation_counter = state.get(
                "stagnation_counter",
                0
            )


            self.last_best_fitness = state.get(
                "last_best_fitness",
                -float("inf")
            )


            print(
                "تم تحميل الحالة السابقة."
            )


        else:

            print(
                "لا توجد حالة محفوظة، سيتم البدء من جديد."
            )

            self._initialize_population()


    # ========================================================
    # MAIN AUTONOMOUS LOOP
    # ========================================================

    def run(
        self,
        epsilon_start: float = 0.1,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995
    ):

        if not self.population:

            self._initialize_population()


        epsilon = epsilon_start

        generation = 0


        print(
            "بدء التطور الذاتي - MAJD AI MASTERMIND ACTIVE"
        )


        while (
            generation
            <
            self.num_generations
        ):

            start_time = time.time()


            self._evaluate_population(
                epsilon=epsilon
            )


            best_fit = (
                self.best_fitness_history[-1]
            )

            avg_fit = (
                self.avg_fitness_history[-1]
            )


            print(
                f"الجيل {generation + 1}/{self.num_generations} | "
                f"أفضل: {best_fit:.2f} | "
                f"متوسط: {avg_fit:.2f} | "
                f"طفرة المستوى: {self.level_mutation_rate:.3f} | "
                f"طفرة الأوزان: {self.weight_mutation_rate:.3f} | "
                f"الوقت: {time.time() - start_time:.2f} ثانية"
            )


            self._adjust_mutation_rates()


            self._evolve()


            epsilon = max(
                epsilon_end,
                epsilon
                *
                epsilon_decay
            )


            if (
                generation + 1
            ) % 10 == 0:

                self._save_state()


            generation += 1


        self._save_state()


        print(
            "اكتمل التطور. أفضل فرد محفوظ في:",
            self.save_dir
        )


        if self.best_individual:

            print(
                f"أفضل لياقة: "
                f"{self.best_individual.fitness:.2f}"
            )


            final_fitness = (
                self.best_individual.evaluate(
                    epsilon=0.0
                )
            )


            print(
                f"التقييم النهائي: "
                f"{final_fitness:.2f}"
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    master = Mastermind(

        population_size=POPULATION_SIZE,

        level_width=LEVEL_WIDTH,

        level_height=LEVEL_HEIGHT,

        max_steps=MAX_STEPS,

        num_generations=NUM_GENERATIONS,

        save_dir="evolution_output",

        resume=False
    )


    master.run()
