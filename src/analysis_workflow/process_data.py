import json
import sys
from typing import Any
import logging
from pathlib import Path

from kestra import Kestra  # type: ignore[import-untyped]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_data(input_file: str) -> dict[str, Any]:
    """
    Process the input data from KV store and generate results.

    Args:
        input_file: Path to the JSON input file containing KV store data

    Returns:
        Dictionary containing processed results
    """
    try:
        # Read input data from file
        with Path(input_file).open("r") as f:
            input_data = json.load(f)

        # Extract data from each analysis type
        results = {key: value["value"]["data"] for key, value in input_data.items()}

        return results

    except FileNotFoundError:
        logging.info(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.info(f"Error: Unable to parse JSON from '{input_file}'")
        sys.exit(1)
    except KeyError as e:
        logging.info(f"Error: Missing expected key in input data: {e}")
        sys.exit(1)
    except Exception as e:
        logging.info(f"Error: Unexpected error occurred: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    # Default input file name (can be overridden by command line argument)
    input_file = "input.json"

    # Allow overriding input file via command line
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    # Process the data
    results = process_data(input_file)

    # Output results using Kestra API
    Kestra.outputs({"results": results})

    logging.info("Data processing completed successfully")


if __name__ == "__main__":
    main()
