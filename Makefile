.PHONY: all
all = help

.venv:
	@echo "Installing project dependencies.."
	@poetry install --no-root


hooks:
	@echo "Adding pre-commit hooks.."
	@poetry run pre-commit install
	

test:
	@echo "Running unit tests.."
	@poetry run pytest

lint:
	@echo "Running lint tests.."
	@poetry run pre-commit run --all-files

clean:
	@echo "Removing .venv"
	@rm -rf .venv
	@poetry env remove --all
mask:
	@echo "Running mask.."
	@poetry run python -m src.back_end.prepare_hazard_mask

compute:
	@echo "Running compute.."
	@poetry run python -m src.back_end.compute_hazard

pipeline:	mask compute

app:
	@echo "Running Streamlit app..."
	@PYTHONPATH=. poetry run streamlit run src/front_end/app.py

help:
	@echo "Available make commands for setup:"
	@echo " make help           - Print help"
	@echo " make .venv          - Install project dependencies"
	@echo " make hooks          - Add pre-commit hooks"
	@echo " make test           - Run unit tests"
	@echo " make lint           - Run lint tests"
	@echo " make clean          - Remove .venv"
	@echo " make mask           - Run the hazard mask preparation"
	@echo " make compute        - Run hazard compute"
	@echo " make pipeline       - Run mask and compute sequentially"
	@echo " make app            - Run the Streamlit application"
