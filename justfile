
# Install python virtual environment
[unix]
venv:
    [ -d .venv ] || python -m venv .venv
    ./.venv/bin/pip install .

# Run unit tests
[unix]
test:
    ./.venv/bin/python -m unittest -v

[windows]
venv:
    [ -d .venv ] || python -m venv .venv
    ./.venv/Scripts/pip install .


# Run unit tests
[windows]
test:
    ./.venv/Scripts/python -m unittest -v
