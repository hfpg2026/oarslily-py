# Package manager
This project uses [uv](https://github.com/astral-sh/uv) to manage python packages.
```
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# Installing deps
Sync the project dependencies with:
```
uv sync
```

This will create a virtual environment and install all required packages.

# venv
Activate with:
```
source .venv/bin/activate
```

# Executing
Run oarslily to run in module mode, as oarslily is packaged as a CLI module.
```
uv run -m oarslily.cli <directory of interest>
```

# Additional notes
`osslili` supports additional drop-in matchers by simply installing them. These packages are addditionally added.

```
python-Levenshtein
python-tlsh
```