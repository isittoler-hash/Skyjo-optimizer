PYTHON ?= python
PIP ?= $(PYTHON) -m pip
ROUND_COUNT ?= 24
SEED ?= 7
POPULATION_SIZE ?= 24
GENERATIONS ?= 20
BASELINE_OUTPUT ?= artifacts/baseline.json
OPTIMIZE_OUTPUT_ROOT ?= artifacts

.PHONY: install test baseline optimize verify

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]

test:
	$(PYTHON) -m pytest

baseline:
	$(PYTHON) -m skyjo_optimizer.cli baseline --rounds $(ROUND_COUNT) --seed $(SEED) --output $(BASELINE_OUTPUT)

optimize:
	$(PYTHON) -m skyjo_optimizer.cli optimize --population-size $(POPULATION_SIZE) --generations $(GENERATIONS) --seed $(SEED) --output-root $(OPTIMIZE_OUTPUT_ROOT)

verify: test baseline optimize
