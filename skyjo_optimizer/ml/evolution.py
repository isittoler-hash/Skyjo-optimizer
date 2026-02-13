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
    holdout_rounds: int = 120
    holdout_every: int = 2
    early_stop_patience: int = 5
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
        if self.config.elite_count <= 0:
            raise ValueError("elite_count must be positive")
        if self.config.elite_count > self.config.population_size:
            raise ValueError("elite_count cannot exceed population_size")

        train_seeds, holdout_seeds = self._build_seed_splits()
        population = [self._random_strategy(rng) for _ in range(self.config.population_size)]
        best_holdout = float("-inf")
        stagnant_generations = 0

        for generation in range(self.config.generations):
            scored = [
                self._score_strategy(
                    strategy=s,
                    situations=situations,
                    generation=generation,
                    eval_rounds=self.config.rounds_per_eval,
                    seed_bank=train_seeds,
                )
                for s in population
            ]
            scored.sort(key=lambda x: x.aggregate_fitness, reverse=True)
            elites = [row.strategy for row in scored[: self.config.elite_count]]

            if generation % self.config.holdout_every == 0:
                holdout_score = self._score_strategy(
                    strategy=elites[0],
                    situations=situations,
                    generation=generation,
                    eval_rounds=self.config.holdout_rounds,
                    seed_bank=holdout_seeds,
                ).aggregate_fitness
                if holdout_score > best_holdout:
                    best_holdout = holdout_score
                    stagnant_generations = 0
                else:
                    stagnant_generations += 1

                if stagnant_generations >= self.config.early_stop_patience:
                    break

            next_population = elites.copy()
            while len(next_population) < self.config.population_size:
                parent = rng.choice(elites)
                next_population.append(self._mutate(parent, rng))
            population = next_population

        final_scores = [
            self._score_strategy(
                strategy=s,
                situations=situations,
                generation=self.config.generations,
                eval_rounds=self.config.holdout_rounds,
                seed_bank=holdout_seeds,
            )
            for s in population
        ]
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
        eval_rounds: int,
        seed_bank: tuple[int, ...],
    ) -> StrategyPerformance:
        scenario_scores: dict[str, float] = {}
        total = 0.0

        for idx, situation in enumerate(situations):
            eval_seed = seed_bank[(generation + idx) % len(seed_bank)]
            result = evaluate_strategy(
                strategy,
                situation,
                rounds=eval_rounds,
                seed=eval_seed,
            )
            scenario_scores[situation.name] = result.fitness
            total += result.fitness

        return StrategyPerformance(
            strategy=strategy,
            scenario_scores=scenario_scores,
            aggregate_fitness=total / len(situations),
        )

    def _build_seed_splits(self) -> tuple[tuple[int, ...], tuple[int, ...]]:
        rng = random.Random(self.config.seed)
        bank = [rng.randrange(1, 10_000_000) for _ in range(24)]
        midpoint = len(bank) // 2
        return tuple(bank[:midpoint]), tuple(bank[midpoint:])

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
