"""
ML Prediction Service
Connects the ML models to the FastAPI backend
"""
import numpy as np
from typing import Dict, List, Any
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.hybrid_model import HybridFailurePredictionModel
from src.monitoring.risk_engine import RiskScoringEngine


class PredictionService:
    """
    Service for making ML predictions
    """
    
    def __init__(self):
        """Initialize prediction service"""
        self.model = None
        self.risk_engine = RiskScoringEngine()
        self.model_loaded = False
    
    def _load_model(self):
        """Load the ML model (lazy loading)"""
        if not self.model_loaded:
            try:
                self.model = HybridFailurePredictionModel()
                self.model_loaded = True
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
                self.model_loaded = False
    
    def predict(self, metrics: Dict[str, float], model_type: str = "hybrid") -> Dict[str, Any]:
        """
        Make a prediction based on input metrics
        
        Args:
            metrics: Dictionary of metric names and values
            model_type: Type of model to use (lstm, xgboost, hybrid)
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Extract key metrics
            accuracy = metrics.get('accuracy', 0.95)
            latency_ms = metrics.get('latency_ms', 50)
            error_rate = metrics.get('error_rate', 0.01)
            cpu_usage = metrics.get('cpu_usage', 0.5)
            memory_usage = metrics.get('memory_usage', 0.6)
            
            # Simple rule-based prediction for demo
            # In production, use the actual ML model
            failure_score = 0.0
            
            # Accuracy impact
            if accuracy < 0.85:
                failure_score += 0.4
            elif accuracy < 0.90:
                failure_score += 0.2
            
            # Latency impact
            if latency_ms > 200:
                failure_score += 0.3
            elif latency_ms > 100:
                failure_score += 0.15
            
            # Error rate impact
            if error_rate > 0.05:
                failure_score += 0.3
            elif error_rate > 0.02:
                failure_score += 0.15
            
            # Resource usage impact
            if cpu_usage > 0.9 or memory_usage > 0.9:
                failure_score += 0.2
            elif cpu_usage > 0.8 or memory_usage > 0.8:
                failure_score += 0.1
            
            # Normalize to 0-1 range
            failure_probability = min(1.0, failure_score)
            
            # Determine risk level
            if failure_probability >= 0.7:
                risk_level = "critical"
            elif failure_probability >= 0.5:
                risk_level = "high"
            elif failure_probability >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Calculate confidence
            confidence = 0.85  # Fixed for demo
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                failure_probability,
                accuracy,
                latency_ms,
                error_rate,
                cpu_usage,
                memory_usage
            )
            
            return {
                'prediction': failure_probability,
                'confidence': confidence,
                'risk_level': risk_level,
                'recommendations': recommendations,
                'metrics_analyzed': len(metrics)
            }
        
        except Exception as e:
            # Fallback prediction
            return {
                'prediction': 0.3,
                'confidence': 0.5,
                'risk_level': 'medium',
                'recommendations': ['Monitor system closely', 'Check logs for anomalies'],
                'error': str(e)
            }
    
    def _generate_recommendations(
        self,
        failure_prob: float,
        accuracy: float,
        latency_ms: float,
        error_rate: float,
        cpu_usage: float,
        memory_usage: float
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if failure_prob >= 0.7:
            recommendations.append("🚨 CRITICAL: Immediate action required to prevent system failure")
        
        if accuracy < 0.85:
            recommendations.append("📉 Retrain model - accuracy below critical threshold")
            recommendations.append("🔍 Investigate data drift and model degradation")
        
        if latency_ms > 200:
            recommendations.append("⚡ Optimize inference pipeline - latency critical")
            recommendations.append("🔧 Consider scaling up compute resources")
        
        if error_rate > 0.05:
            recommendations.append("❌ High error rate detected - review error logs")
            recommendations.append("🛠️ Check data validation and error handling")
        
        if cpu_usage > 0.9 or memory_usage > 0.9:
            recommendations.append("💻 Resource usage critical - scale infrastructure")
            recommendations.append("📊 Implement resource monitoring and alerts")
        
        if not recommendations:
            recommendations.append("✅ System operating normally")
            recommendations.append("📊 Continue monitoring key metrics")
        
        return recommendations[:5]  # Limit to top 5
    
    def batch_predict(self, metrics_list: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Make predictions for multiple metric sets
        
        Args:
            metrics_list: List of metric dictionaries
            
        Returns:
            List of prediction results
        """
        return [self.predict(metrics) for metrics in metrics_list]
