"""CLI entry: python -m scripts.build_data"""

from src.pipeline.build_dataset import build_all

if __name__ == "__main__":
    build_all()
