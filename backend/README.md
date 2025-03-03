# FastAPI Starter

Look at the [FastAPI documentation](https://fastapi.tiangolo.com) to learn more.

## Setup

### Setup for [uv](https://docs.astral.sh/uv/) users

```bash
# Install dependencies
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Setup for [pip](https://pip.pypa.io/en/stable/getting-started/) users

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install .
```

## Running the Project

You can run backend with `fastapi`:

```bash
fastapi dev main.py
```

Or with `uvicorn` directly:

```bash
uvicorn main:app --reload
```
