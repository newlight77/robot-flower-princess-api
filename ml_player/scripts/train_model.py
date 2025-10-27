#!/usr/bin/env python3
"""
Training script for ML models.

Usage:
    python scripts/train_model.py [OPTIONS]

Options:
    --model-type: Type of model (random_forest, gradient_boosting) [default: random_forest]
    --data-dir: Directory with training data [default: data/training]
    --model-dir: Directory to save models [default: models]
    --test-size: Test set size [default: 0.2]
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hexagons.mltraining.domain.ml import GameDataCollector, ModelTrainer
from shared.logging import logger


def main() -> None:
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train ML model for action prediction")
    parser.add_argument(
        "--model-type",
        type=str,
        default="random_forest",
        choices=["random_forest", "gradient_boosting"],
        help="Type of model to train",
    )
    parser.add_argument("--data-dir", type=str, default="data/training", help="Directory with training data")
    parser.add_argument("--model-dir", type=str, default="models", help="Directory to save models")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set size (0-1)")
    parser.add_argument(
        "--n-estimators", type=int, default=100, help="Number of estimators for ensemble models"
    )
    parser.add_argument("--max-depth", type=int, default=10, help="Maximum depth of trees")

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("ML Model Training")
    logger.info("=" * 60)
    logger.info(f"Model type: {args.model_type}")
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Model directory: {args.model_dir}")
    logger.info(f"Test size: {args.test_size}")
    logger.info("=" * 60)

    # Initialize components
    collector = GameDataCollector(data_dir=args.data_dir)
    trainer = ModelTrainer(model_dir=args.model_dir)

    # Check data availability
    stats = collector.get_statistics()
    logger.info(f"Training data statistics: {stats}")

    if stats["total_samples"] < 100:
        logger.error(f"Insufficient training data: {stats['total_samples']} samples (minimum: 100)")
        logger.error("Please collect more data before training")
        sys.exit(1)

    try:
        # Train model
        result = trainer.train_from_collector(
            collector,
            model_type=args.model_type,
            test_size=args.test_size,
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
        )

        # Print results
        metrics = result["metrics"]
        logger.info("=" * 60)
        logger.info("Training completed successfully!")
        logger.info("=" * 60)
        logger.info(f"Train accuracy: {metrics['train_accuracy']:.4f}")
        logger.info(f"Test accuracy: {metrics['test_accuracy']:.4f}")
        logger.info(f"Train samples: {metrics['train_samples']}")
        logger.info(f"Test samples: {metrics['test_samples']}")
        logger.info(f"Model saved to: {result['model_path']}")

        # Print top features
        if "feature_importance" in metrics:
            logger.info("\nTop 10 Features:")
            for idx, (feature, importance) in enumerate(metrics["feature_importance"].items(), 1):
                logger.info(f"  {idx}. {feature}: {importance:.4f}")

        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
