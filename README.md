# Generic Decorator

A Python utility project that provides a reusable, extensible, and robust decorator to monitor function executions with features like structured logging, system resource monitoring, input/output validation, and error handling. This decorator is especially useful for debugging, profiling, and enforcing data contracts in production-grade systems.

## Features

* **Input/Output Validation**: Validates inputs and outputs using Python type hints and Pydantic models.
* **Structured Logging**: Logs metadata-rich execution results using `structlog`.
* **Performance Monitoring**: Captures CPU usage, memory usage, and execution time.
* **Error Handling**: Catches and logs exceptions with tracebacks.
* **Environment Configurable**: Controls behavior using `.env` variables.

## Requirements

* Python >= 3.11

## Installation

Install dependencies using `uv`:

```bash
uv pip install -r requirements.txt
```

Or using `pyproject.toml`:

```bash
uv venv
uv pip install -e .
```

## Environment Variables

Create a `.env` file in the root directory to configure the decorator behavior:

```env
LOG_LEVEL=10
VALIDATE_INPUT=True
VALIDATE_OUTPUT=True
LOG_EXECUTION=True
RAW_RESULT=False
```

## Usage

```bash
uv pip install .
uv run main.py
```

## Dependencies

* `psutil`: System monitoring
* `pydantic`: Data validation
* `python-dotenv`: Environment variable loading
* `structlog`: Structured logging

---

## Contribution

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
