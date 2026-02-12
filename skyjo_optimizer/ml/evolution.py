from __future__ import annotations

import random
from dataclasses import dataclass

from skyjo_optimizer.agents.heuristic import HeuristicStrategy
from skyjo_optimizer.simulation.evaluator import evaluate_strategy
from skyjo_optimizer.simulation.scenarios import GameSituation


@dataclass(frozen=True)
class EvolutionConfig:
    population_size: int = 24
    generations: int = 20
    elite_count: int = 6
    mutation_sigma: float = 0.12
    rounds_per_eval: int = 120
    seed: int = 7


@dataclass(frozen=True)
class StrategyPerformance:
    strategy: HeuristicStrategy
    scenario_scores: dict[str, float]
    aggregate_fitness: float


class EvolutionOptimizer:
    def __init__(self, config: EvolutionConfig | None = None) -> None:
        self.config = config or EvolutionConfig()

    def optimize(self, situations: list[GameSituation]) -> StrategyPerformance:
        if not situations:
            raise ValueError("at least one game situation is required")

        rng = random.Random(self.config.seed)
        population = [self._random_strategy(rng) for _ in range(self.config.population_size)]

        for generation in range(self.config.generations):
            scored = [self._score_strategy(s, situations, generation) for s in population]
            scored.sort(key=lambda x: x.aggregate_fitness, reverse=True)
            elites = [row.strategy for row in scored[: self.config.elite_count]]

            next_population = elites.copy()
            while len(next_population) < self.config.population_size:
                parent = rng.choice(elites)
                next_population.append(self._mutate(parent, rng))
            population = next_population

        final_scores = [self._score_strategy(s, situations, self.config.generations) for s in population]
        final_scores.sort(key=lambda x: x.aggregate_fitness, reverse=True)
        return final_scores[0]

    def select_best_for_situation(
        self,
        candidates: list[HeuristicStrategy],
        situation: GameSituation,
        rounds: int = 160,
    ) -> StrategyPerformance:
        if not candidates:
            raise ValueError("at least one candidate strategy is required")

        scored = [
            self._single_situation_score(strategy, situation, rounds, eval_seed=idx)
            for idx, strategy in enumerate(candidates)
        ]
        scored.sort(key=lambda x: x.aggregate_fitness, reverse=True)
        return scored[0]

    def _score_strategy(
        self,
        strategy: HeuristicStrategy,
        situations: list[GameSituation],
        generation: int,
    ) -> StrategyPerformance:
        scenario_scores: dict[str, float] = {}
        total = 0.0

        for idx, situation in enumerate(situations):
            eval_seed = self.config.seed + generation * 1000 + idx * 37
            result = evaluate_strategy(
                strategy,
                situation,
                rounds=self.config.rounds_per_eval,
                seed=eval_seed,
            )
            scenario_scores[situation.name] = result.fitness
            total += result.fitness

        return StrategyPerformance(
            strategy=strategy,
            scenario_scores=scenario_scores,
            aggregate_fitness=total / len(situations),
        )

    def _single_situation_score(
        self,
        strategy: HeuristicStrategy,
        situation: GameSituation,
        rounds: int,
        eval_seed: int,
    ) -> StrategyPerformance:
        result = evaluate_strategy(
            strategy,
            situation,
            rounds=rounds,
            seed=self.config.seed + eval_seed,
        )
        return StrategyPerformance(
            strategy=strategy,
            scenario_scores={situation.name: result.fitness},
            aggregate_fitness=result.fitness,
        )

    @staticmethod
    def _random_strategy(rng: random.Random) -> HeuristicStrategy:
        return HeuristicStrategy(
            risk_tolerance=rng.random(),
            reveal_priority=rng.random(),
            column_focus=rng.random(),
            discard_aggression=rng.random(),
        )

    def _mutate(self, parent: HeuristicStrategy, rng: random.Random) -> HeuristicStrategy:
        child = HeuristicStrategy(
            risk_tolerance=parent.risk_tolerance + rng.gauss(0, self.config.mutation_sigma),
            reveal_priority=parent.reveal_priority + rng.gauss(0, self.config.mutation_sigma),
            column_focus=parent.column_focus + rng.gauss(0, self.config.mutation_sigma),
            discard_aggression=parent.discard_aggression
            + rng.gauss(0, self.config.mutation_sigma),
        )
        return child.clipped()
