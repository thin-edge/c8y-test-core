
# Note: Windows stores virtual environment scripts under Scripts/ directory instead of bin/
# and uses 'python'/'pip' instead of 'python3'/'pip3'
venv_bin := if os_family() == "windows" { ".venv/Scripts" } else { ".venv/bin" }
python := if os_family() == "windows" { "python" } else { "python3" }
pip := if os_family() == "windows" { "pip" } else { "pip3" }

# Install python virtual environment
venv:
    [ -d .venv ] || {{python}} -m venv .venv
    {{venv_bin}}/{{pip}} install .

# Run unit tests
test:
    {{venv_bin}}/{{python}} -m unittest -v
