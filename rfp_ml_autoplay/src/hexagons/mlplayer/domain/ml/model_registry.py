"""
Model Registry for managing trained models.

Handles model versioning, loading, and serving.
"""

import json
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from shared.logging import get_logger

logger = get_logger("ModelRegistry")


@dataclass
class ModelMetadata:
    """Metadata for a registered model."""

    name: str
    version: str
    model_type: str
    created_at: str
    test_accuracy: float
    train_samples: int
    test_samples: int
    model_path: str
    metrics_path: str


class ModelRegistry:
    """Registry for managing and serving ML models."""

    def __init__(self, model_dir: str = "models"):
        """
        Initialize model registry.

        Args:
            model_dir: Directory containing trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Any] = {}
        logger.info(f"ModelRegistry initialized with model_dir={self.model_dir}")

    def list_models(self) -> list[ModelMetadata]:
        """
        List all registered models.

        Returns:
            List of model metadata
        """
        models = []

        for model_file in self.model_dir.glob("*.pkl"):
            metrics_file = model_file.with_name(f"{model_file.stem}_metrics.json")

            if not metrics_file.exists():
                logger.warning(f"Metrics file not found for {model_file}")
                continue

            try:
                with open(metrics_file) as f:
                    metrics = json.load(f)

                metadata = ModelMetadata(
                    name=model_file.stem,
                    version=metrics.get("timestamp", "unknown"),
                    model_type=metrics.get("model_type", "unknown"),
                    created_at=metrics.get("timestamp", "unknown"),
                    test_accuracy=metrics.get("test_accuracy", 0.0),
                    train_samples=metrics.get("train_samples", 0),
                    test_samples=metrics.get("test_samples", 0),
                    model_path=str(model_file),
                    metrics_path=str(metrics_file),
                )
                models.append(metadata)

            except Exception as e:
                logger.warning(f"Failed to load metadata for {model_file}: {e}")
                continue

        # Sort by test accuracy (descending)
        models.sort(key=lambda m: m.test_accuracy, reverse=True)

        logger.info(f"ModelRegistry.list_models: Found {len(models)} models")
        logger.info(f"ModelRegistry.list_models: Found models: {[m.name for m in models]}")

        return models

    def get_best_model(self, model_type: str | None = None) -> ModelMetadata | None:
        """
        Get the best performing model.

        Args:
            model_type: Filter by model type (optional)

        Returns:
            Best model metadata, or None if no models found
        """
        logger.info(f"ModelRegistry.get_best_model: Getting best model with model_type={model_type}")
        models = self.list_models()

        if model_type:
            models = [m for m in models if m.model_type == model_type]

        if not models:
            return None

        logger.info(f"ModelRegistry.get_best_model: Found {len(models)} models")
        logger.info(f"ModelRegistry.get_best_model: best model: {models[0].name}")
        return models[0]  # Already sorted by test_accuracy

    def load_model(self, model_name: str) -> Any:
        """
        Load a model by name.

        Args:
            model_name: Name of the model (without .pkl extension)

        Returns:
            Loaded model
        """
        logger.info(f"ModelRegistry.load_model: Loading model: {model_name}")
        # Check cache first
        if model_name in self._cache:
            logger.debug(f"Model {model_name} loaded from cache")
            return self._cache[model_name]

        # Load from disk
        model_path = self.model_dir / f"{model_name}.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        # Cache the model
        self._cache[model_name] = model

        logger.info(f"ModelRegistry.load_model: Model loaded: {model_name} and cached: {model_name in self._cache}")
        return model

    def load_best_model(self, model_type: str | None = None) -> tuple[Any, ModelMetadata] | tuple[None, None]:
        """
        Load the best performing model.

        Args:
            model_type: Filter by model type (optional)

        Returns:
            Tuple of (model, metadata), or (None, None) if no models found
        """
        best_metadata = self.get_best_model(model_type)

        if not best_metadata:
            logger.warning("No models found in registry")
            return None, None

        model = self.load_model(best_metadata.name)

        logger.info(f"Loaded best model: {best_metadata.name} (accuracy={best_metadata.test_accuracy:.4f})")

        return model, best_metadata

    def get_model_metrics(self, model_name: str) -> dict[str, Any]:
        """
        Get metrics for a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model metrics
        """
        logger.info(f"ModelRegistry.get_model_metrics: Getting metrics for model: {model_name}")
        metrics_path = self.model_dir / f"{model_name}_metrics.json"

        if not metrics_path.exists():
            raise FileNotFoundError(f"Metrics not found: {metrics_path}")

        with open(metrics_path) as f:
            metrics = json.load(f)

        logger.info(f"ModelRegistry.get_model_metrics: Metrics found: {metrics}")
        return metrics

    def register_model(
        self,
        model: Any,
        metrics: dict[str, Any],
        name: str,
        tags: dict[str, str] | None = None,
    ) -> ModelMetadata:
        """
        Register a new model in the registry.

        Args:
            model: Trained model
            metrics: Evaluation metrics
            name: Model name
            tags: Optional tags for the model

        Returns:
            Model metadata
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_name = f"{name}_{timestamp}"

        logger.info(f"ModelRegistry.register_model: Registering model: {model_name}")

        # Add tags to metrics
        if tags:
            metrics["tags"] = tags

        # Save model
        model_path = self.model_dir / f"{model_name}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        # Save metrics
        metrics_path = self.model_dir / f"{model_name}_metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"ModelRegistry.register_model: Model saved: {model_name}")

        metadata = ModelMetadata(
            name=model_name,
            version=timestamp,
            model_type=metrics.get("model_type", "unknown"),
            created_at=timestamp,
            test_accuracy=metrics.get("test_accuracy", 0.0),
            train_samples=metrics.get("train_samples", 0),
            test_samples=metrics.get("test_samples", 0),
            model_path=str(model_path),
            metrics_path=str(metrics_path),
        )

        logger.info(f"Model registered: {model_name} (accuracy={metadata.test_accuracy:.4f})")

        return metadata

    def clear_cache(self) -> None:
        """Clear the model cache."""
        self._cache.clear()
        logger.info("ModelRegistry.clear_cache: Model cache cleared")
