"""Convenience entry point — train the model from responses.csv at the repo root."""

from pathlib import Path
import subprocess
import sys


def main() -> None:
    repo = Path(__file__).resolve().parent
    csv_path = repo / "responses.csv"
    if not csv_path.exists():
        print("responses.csv not found at repo root.", file=sys.stderr)
        sys.exit(1)
    cmd = [
        sys.executable,
        "-m",
        "ml.train_from_real_data",
        str(csv_path),
    ]
    subprocess.run(cmd, cwd=repo / "fastapi_ml", check=True)


if __name__ == "__main__":
    main()
