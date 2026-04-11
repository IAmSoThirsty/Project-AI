"""
Capacity Planner - Predict resource needs based on historical usage
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np

from .types import CapacityPrediction, ResourceQuota

logger = logging.getLogger(__name__)


class CapacityPlanner:
    """
    Predicts future resource needs based on historical usage patterns.
    
    Uses time-series analysis to forecast:
    - CPU requirements
    - Memory requirements
    - GPU requirements
    """
    
    def __init__(
        self,
        history_days: int = 30,
        prediction_horizons: List[int] = [1, 6, 12, 24],
    ):
        """
        Initialize capacity planner.
        
        Args:
            history_days: Days of history to maintain
            prediction_horizons: Forecast horizons in hours
        """
        self.history_days = history_days
        self.prediction_horizons = prediction_horizons
        
        self._usage_history: List[Tuple[datetime, ResourceQuota]] = []
        self._predictions: Dict[int, CapacityPrediction] = {}
        
        logger.info(
            f"Initialized CapacityPlanner: history={history_days} days, "
            f"horizons={prediction_horizons}h"
        )
    
    async def record_usage(
        self,
        timestamp: datetime,
        cpu_cores: float,
        memory_gb: float,
        gpu_count: int = 0,
    ) -> None:
        """
        Record resource usage at a point in time.
        
        Args:
            timestamp: Time of measurement
            cpu_cores: CPU cores used
            memory_gb: Memory GB used
            gpu_count: GPUs used
        """
        usage = ResourceQuota(
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            gpu_count=gpu_count,
        )
        
        self._usage_history.append((timestamp, usage))
        
        # Trim old history
        cutoff = datetime.utcnow() - timedelta(days=self.history_days)
        self._usage_history = [
            (ts, quota) for ts, quota in self._usage_history
            if ts >= cutoff
        ]
    
    async def predict(
        self,
        horizon_hours: int,
        method: str = "linear",
    ) -> CapacityPrediction:
        """
        Predict resource needs for a future time horizon.
        
        Args:
            horizon_hours: Hours into the future
            method: Prediction method ("linear", "exponential", "seasonal")
            
        Returns:
            Capacity prediction
        """
        if len(self._usage_history) < 10:
            logger.warning("Insufficient history for prediction")
            return CapacityPrediction(
                timestamp=datetime.utcnow() + timedelta(hours=horizon_hours),
                predicted_cpu_cores=0.0,
                predicted_memory_gb=0.0,
                predicted_gpu_count=0,
                confidence=0.0,
                horizon_hours=horizon_hours,
            )
        
        if method == "linear":
            prediction = await self._predict_linear(horizon_hours)
        elif method == "exponential":
            prediction = await self._predict_exponential(horizon_hours)
        elif method == "seasonal":
            prediction = await self._predict_seasonal(horizon_hours)
        else:
            raise ValueError(f"Unknown prediction method: {method}")
        
        self._predictions[horizon_hours] = prediction
        
        logger.info(
            f"Predicted for {horizon_hours}h: CPU={prediction.predicted_cpu_cores:.1f}, "
            f"Memory={prediction.predicted_memory_gb:.1f}GB, "
            f"GPU={prediction.predicted_gpu_count} (confidence={prediction.confidence:.2f})"
        )
        
        return prediction
    
    async def _predict_linear(self, horizon_hours: int) -> CapacityPrediction:
        """Linear trend prediction"""
        # Extract time series
        timestamps = [ts for ts, _ in self._usage_history]
        cpu_values = [quota.cpu_cores for _, quota in self._usage_history]
        memory_values = [quota.memory_gb for _, quota in self._usage_history]
        gpu_values = [quota.gpu_count for _, quota in self._usage_history]
        
        # Convert timestamps to hours from start
        start_time = timestamps[0]
        x = np.array([(ts - start_time).total_seconds() / 3600 for ts in timestamps])
        
        # Fit linear regression
        cpu_pred = self._linear_regression(x, cpu_values, horizon_hours)
        memory_pred = self._linear_regression(x, memory_values, horizon_hours)
        gpu_pred = self._linear_regression(x, gpu_values, horizon_hours)
        
        # Calculate confidence based on variance
        cpu_std = np.std(cpu_values)
        confidence = max(0.0, 1.0 - (cpu_std / max(np.mean(cpu_values), 1.0)))
        
        return CapacityPrediction(
            timestamp=datetime.utcnow() + timedelta(hours=horizon_hours),
            predicted_cpu_cores=max(0.0, cpu_pred),
            predicted_memory_gb=max(0.0, memory_pred),
            predicted_gpu_count=max(0, int(gpu_pred)),
            confidence=confidence,
            horizon_hours=horizon_hours,
        )
    
    async def _predict_exponential(self, horizon_hours: int) -> CapacityPrediction:
        """Exponential smoothing prediction"""
        alpha = 0.3  # Smoothing factor
        
        cpu_values = [quota.cpu_cores for _, quota in self._usage_history]
        memory_values = [quota.memory_gb for _, quota in self._usage_history]
        gpu_values = [quota.gpu_count for _, quota in self._usage_history]
        
        # Apply exponential smoothing
        cpu_smoothed = self._exponential_smooth(cpu_values, alpha)
        memory_smoothed = self._exponential_smooth(memory_values, alpha)
        gpu_smoothed = self._exponential_smooth(gpu_values, alpha)
        
        # Project forward
        cpu_pred = cpu_smoothed[-1]
        memory_pred = memory_smoothed[-1]
        gpu_pred = gpu_smoothed[-1]
        
        # Calculate trend
        if len(cpu_smoothed) >= 2:
            cpu_trend = cpu_smoothed[-1] - cpu_smoothed[-2]
            memory_trend = memory_smoothed[-1] - memory_smoothed[-2]
            gpu_trend = gpu_smoothed[-1] - gpu_smoothed[-2]
            
            cpu_pred += cpu_trend * horizon_hours
            memory_pred += memory_trend * horizon_hours
            gpu_pred += gpu_trend * horizon_hours
        
        confidence = 0.7  # Fixed confidence for exponential
        
        return CapacityPrediction(
            timestamp=datetime.utcnow() + timedelta(hours=horizon_hours),
            predicted_cpu_cores=max(0.0, cpu_pred),
            predicted_memory_gb=max(0.0, memory_pred),
            predicted_gpu_count=max(0, int(gpu_pred)),
            confidence=confidence,
            horizon_hours=horizon_hours,
        )
    
    async def _predict_seasonal(self, horizon_hours: int) -> CapacityPrediction:
        """Seasonal pattern prediction (daily/weekly cycles)"""
        # Find similar historical periods
        target_hour = (datetime.utcnow() + timedelta(hours=horizon_hours)).hour
        target_day = (datetime.utcnow() + timedelta(hours=horizon_hours)).weekday()
        
        # Filter to similar times
        similar_periods = [
            quota for ts, quota in self._usage_history
            if ts.hour == target_hour and ts.weekday() == target_day
        ]
        
        if len(similar_periods) < 3:
            # Fall back to linear
            return await self._predict_linear(horizon_hours)
        
        # Average similar periods
        avg_cpu = np.mean([q.cpu_cores for q in similar_periods])
        avg_memory = np.mean([q.memory_gb for q in similar_periods])
        avg_gpu = np.mean([q.gpu_count for q in similar_periods])
        
        # Higher confidence for seasonal patterns
        confidence = min(0.9, len(similar_periods) / 10.0)
        
        return CapacityPrediction(
            timestamp=datetime.utcnow() + timedelta(hours=horizon_hours),
            predicted_cpu_cores=avg_cpu,
            predicted_memory_gb=avg_memory,
            predicted_gpu_count=int(avg_gpu),
            confidence=confidence,
            horizon_hours=horizon_hours,
        )
    
    def _linear_regression(
        self,
        x: np.ndarray,
        y: List[float],
        future_x: float,
    ) -> float:
        """Simple linear regression"""
        y_array = np.array(y)
        
        # Calculate slope and intercept
        x_mean = np.mean(x)
        y_mean = np.mean(y_array)
        
        numerator = np.sum((x - x_mean) * (y_array - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        if denominator == 0:
            return y_mean
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Predict
        prediction = slope * (x[-1] + future_x) + intercept
        return prediction
    
    def _exponential_smooth(
        self,
        values: List[float],
        alpha: float,
    ) -> List[float]:
        """Apply exponential smoothing"""
        if not values:
            return []
        
        smoothed = [values[0]]
        for value in values[1:]:
            smoothed.append(alpha * value + (1 - alpha) * smoothed[-1])
        
        return smoothed
    
    async def get_all_predictions(
        self,
        method: str = "linear",
    ) -> Dict[int, CapacityPrediction]:
        """
        Get predictions for all configured horizons.
        
        Args:
            method: Prediction method
            
        Returns:
            Dictionary mapping horizon to prediction
        """
        predictions = {}
        
        for horizon in self.prediction_horizons:
            predictions[horizon] = await self.predict(horizon, method)
        
        return predictions
    
    async def get_capacity_report(self) -> Dict[str, any]:
        """
        Generate capacity planning report.
        
        Returns:
            Report dictionary
        """
        if len(self._usage_history) < 10:
            return {
                "status": "insufficient_data",
                "message": "Need at least 10 data points",
                "data_points": len(self._usage_history),
            }
        
        # Current usage
        _, current_usage = self._usage_history[-1]
        
        # Historical statistics
        cpu_values = [q.cpu_cores for _, q in self._usage_history]
        memory_values = [q.memory_gb for _, q in self._usage_history]
        
        return {
            "status": "ok",
            "current_usage": {
                "cpu_cores": current_usage.cpu_cores,
                "memory_gb": current_usage.memory_gb,
                "gpu_count": current_usage.gpu_count,
            },
            "statistics": {
                "cpu_avg": np.mean(cpu_values),
                "cpu_max": np.max(cpu_values),
                "cpu_min": np.min(cpu_values),
                "memory_avg": np.mean(memory_values),
                "memory_max": np.max(memory_values),
                "memory_min": np.min(memory_values),
            },
            "data_points": len(self._usage_history),
            "predictions": {
                h: p for h, p in self._predictions.items()
            },
        }
