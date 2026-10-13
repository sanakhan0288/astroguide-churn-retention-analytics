"""
AstroGuide AI - Master End-to-End Analytics Pipeline
====================================================
Orchestrates the complete data engineering, modeling, analysis, and testing
workflow from scratch with a single command.

Execution Stages:
1. Synthetic Data Generation (src/generate_data.py)
2. Automated Data Quality & Validation (src/validate_data.py)
3. Star Schema Dimensional Preparation (src/prepare_data.py)
4. SQLite Database Loading (src/load_database.py)
5. SQL Analytics Execution (src/run_sql_analysis.py)
6. Churn Prediction & Risk Scoring (src/train_model.py)
7. DAX Measure Reconciliation (src/verify_dax_measures.py)
8. Automated Pytest Verification Suite (tests/)

Usage:
    python src/run_pipeline.py [--users 10000] [--seed 42]

Author: AstroGuide Analytics Team
"""

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("PipelineMaster")


def run_stage(stage_num: int, name: str, cmd: list) -> bool:
    """Run a pipeline stage with timing and error trapping."""
    print("\n" + "=" * 80)
    logger.info("STAGE %d/8: %s", stage_num, name.upper())
    logger.info("Command: %s", " ".join(cmd))
    print("=" * 80)

    start_time = time.time()
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=False)
    elapsed = time.time() - start_time

    if result.returncode != 0:
        logger.error("❌ STAGE %d FAILED (%s) with exit code %d after %.2fs", stage_num, name, result.returncode, elapsed)
        return False
    else:
        logger.info("✅ STAGE %d COMPLETED (%s) in %.2fs", stage_num, name, elapsed)
        return True


def main():
    parser = argparse.ArgumentParser(description="Execute complete AstroGuide AI analytics pipeline.")
    parser.add_argument("--users", type=int, default=10000, help="Number of users to generate (default: 10000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip final pytest test execution")
    args = parser.parse_args()

    pipeline_start = time.time()
    python_bin = sys.executable

    print("\n" + "#" * 80)
    print("   ASTROGUIDE AI - MASTER END-TO-END ANALYTICS & REPRODUCIBILITY PIPELINE")
    print("#" * 80)
    logger.info("Configuration: %d Users | Random Seed: %d | Python: %s", args.users, args.seed, python_bin)

    stages = [
        (1, "Synthetic Relational Data Generation", [
            python_bin, "src/generate_data.py", "--users", str(args.users), "--seed", str(args.seed)
        ]),
        (2, "Data Quality & Relational Validation", [
            python_bin, "src/validate_data.py"
        ]),
        (3, "Star Schema Dimensional Data Preparation", [
            python_bin, "src/prepare_data.py"
        ]),
        (4, "SQLite Database Loading", [
            python_bin, "src/load_database.py"
        ]),
        (5, "SQL Analytical Queries Execution", [
            python_bin, "src/run_sql_analysis.py"
        ]),
        (6, "Machine Learning Churn Prediction & Risk Scoring", [
            python_bin, "src/train_model.py"
        ]),
        (7, "DAX Measures Independent Reconciliation", [
            python_bin, "src/verify_dax_measures.py"
        ]),
    ]

    if not args.skip_tests:
        stages.append(
            (8, "Automated Test Suite (Pytest)", [
                python_bin, "-m", "pytest", "tests/", "-v"
            ])
        )

    for stage_num, name, cmd in stages:
        success = run_stage(stage_num, name, cmd)
        if not success:
            logger.critical("Pipeline aborted due to failure in Stage %d: %s", stage_num, name)
            sys.exit(1)

    total_time = time.time() - pipeline_start
    print("\n" + "#" * 80)
    logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY! All stages passed in %.2f seconds.", total_time)
    print("#" * 80 + "\n")


if __name__ == "__main__":
    main()
