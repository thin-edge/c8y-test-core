
# Install python virtual environment
[unix]
venv:
    [ -d .venv ] || python3 -m venv .venv
    ./.venv/bin/pip3 install .

# Run unit tests
[unix]
test:
    ./.venv/bin/python3 -m unittest -v

[windows]
venv:
    [ -d .venv ] || python3 -m venv .venv
    ./.venv/Scripts/pip3 install .


# Run unit tests
[windows]
test:
    ./.venv/Scripts/python3 -m unittest -v
