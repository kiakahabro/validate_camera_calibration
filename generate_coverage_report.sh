source .venv/bin/activate
$(which python) -m pytest --cov=./ tests --cov-report xml