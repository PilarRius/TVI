"""CLI: ingest public PVSIS Evaluation/Follow-Up reports into data/raw/pvs_indicators.csv"""

from src.ingestion.pvsis_public import ingest_public_pvs

if __name__ == "__main__":
    ingest_public_pvs()
