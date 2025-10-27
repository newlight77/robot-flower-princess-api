"""
Model Training for ML-based Action Prediction.

Trains and evaluates machine learning models on collected game data.
"""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from shared.logging import logger

from .data_collector import GameDataCollector
from .feature_engineer import FeatureEngineer


class ModelTrainer:
    """Trains ML models for action prediction."""

    def __init__(self, model_dir: str = "models"):
        """
        Initialize model trainer.

        Args:
            model_dir: Directory to save trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.feature_engineer = FeatureEngineer()
        logger.info(f"ModelTrainer initialized with model_dir={self.model_dir}")

    def prepare_dataset(self, samples: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
        """
        Prepare training dataset from collected samples.

        Args:
            samples: List of collected game samples

        Returns:
            Tuple of (features, labels)
        """
        X_list = []  # noqa: N806 (ML convention: X for features)
        y_list = []

        for sample in samples:
            try:
                # Extract features
                features = self.feature_engineer.extract_features(sample["game_state"])
                X_list.append(features)

                # Encode action as label
                label = self.feature_engineer.encode_action(sample["action"], sample.get("direction"))
                logger.info(f"Encoded action: {sample['action']} {sample.get('direction')} -> {label}")
                y_list.append(label)

            except Exception as e:
                logger.warning(f"Failed to process sample: {e}")
                continue

        X = np.array(X_list)  # noqa: N806 (ML convention: X for features)
        y = np.array(y_list)

        logger.info(f"Prepared dataset: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y

    def train_random_forest(
        self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, **kwargs: Any  # noqa: N803 (ML convention)
    ) -> dict[str, Any]:
        """
        Train a Random Forest classifier.

        Args:
            X: Feature matrix
            y: Labels
            test_size: Fraction of data for testing
            **kwargs: Additional parameters for RandomForestClassifier

        Returns:
            Dictionary with model and metrics
        """
        logger.info("Training Random Forest model...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)  # noqa: N806

        # Default hyperparameters
        params = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": 42,
            "n_jobs": -1,
        }
        params.update(kwargs)

        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        # Evaluate
        metrics = self._evaluate_model(model, X_train, y_train, X_test, y_test)
        metrics["model_type"] = "RandomForest"
        metrics["hyperparameters"] = params

        logger.info(f"Random Forest trained: accuracy={metrics['test_accuracy']:.4f}")

        return {"model": model, "metrics": metrics}

    def train_gradient_boosting(
        self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, **kwargs: Any  # noqa: N803 (ML convention)
    ) -> dict[str, Any]:
        """
        Train a Gradient Boosting classifier.

        Args:
            X: Feature matrix
            y: Labels
            test_size: Fraction of data for testing
            **kwargs: Additional parameters for GradientBoostingClassifier

        Returns:
            Dictionary with model and metrics
        """
        logger.info("Training Gradient Boosting model...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)  # noqa: N806

        # Default hyperparameters
        params = {
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 5,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": 42,
        }
        params.update(kwargs)

        # Train model
        model = GradientBoostingClassifier(**params)
        model.fit(X_train, y_train)

        # Evaluate
        metrics = self._evaluate_model(model, X_train, y_train, X_test, y_test)
        metrics["model_type"] = "GradientBoosting"
        metrics["hyperparameters"] = params

        logger.info(f"Gradient Boosting trained: accuracy={metrics['test_accuracy']:.4f}")

        return {"model": model, "metrics": metrics}

    def _evaluate_model(
        self, model: Any, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray  # noqa: N803
    ) -> dict[str, Any]:
        """
        Evaluate trained model.

        Args:
            model: Trained model
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary with evaluation metrics
        """
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        # Metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        test_accuracy = accuracy_score(y_test, y_test_pred)

        # Classification report
        report = classification_report(y_test, y_test_pred, output_dict=True, zero_division=0)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_test_pred)

        metrics = {
            "train_accuracy": float(train_accuracy),
            "test_accuracy": float(test_accuracy),
            "train_samples": len(y_train),
            "test_samples": len(y_test),
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Feature importance (if available)
        if hasattr(model, "feature_importances_"):
            feature_names = self.feature_engineer.get_feature_names()
            importances = model.feature_importances_
            feature_importance = dict(zip(feature_names, [float(imp) for imp in importances]))
            metrics["feature_importance"] = dict(
                sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            )

        return metrics

    def save_model(self, model: Any, metrics: dict[str, Any], name: str = "model") -> str:
        """
        Save trained model and metrics.

        Args:
            model: Trained model
            metrics: Evaluation metrics
            name: Model name

        Returns:
            Path to saved model
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_name = f"{name}_{timestamp}"

        # Save model
        model_path = self.model_dir / f"{model_name}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        # Save metrics
        metrics_path = self.model_dir / f"{model_name}_metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Model saved to {model_path}")
        return str(model_path)

    def load_model(self, model_path: str) -> Any:
        """
        Load a trained model.

        Args:
            model_path: Path to model file

        Returns:
            Loaded model
        """
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        logger.info(f"Model loaded from {model_path}")
        return model

    def train_from_collector(
        self, collector: GameDataCollector, model_type: str = "random_forest", **kwargs: Any
    ) -> dict[str, Any]:
        """
        Train model from collected data.

        Args:
            collector: Data collector instance
            model_type: Type of model to train ('random_forest' or 'gradient_boosting')
            **kwargs: Additional parameters for model training

        Returns:
            Dictionary with model and metrics
        """
        # Load samples
        samples = collector.load_samples()

        if len(samples) < 100:
            raise ValueError(f"Insufficient training data: {len(samples)} samples (minimum: 100)")

        # Prepare dataset
        X, y = self.prepare_dataset(samples)  # noqa: N806 (ML convention: X for features)

        # Train model
        if model_type == "random_forest":
            result = self.train_random_forest(X, y, **kwargs)
        elif model_type == "gradient_boosting":
            result = self.train_gradient_boosting(X, y, **kwargs)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Save model
        model_path = self.save_model(result["model"], result["metrics"], name=model_type)
        result["model_path"] = model_path

        return result
