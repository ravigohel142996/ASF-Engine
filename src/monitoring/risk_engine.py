"""
Risk Scoring Engine
Calculates risk scores and provides root cause analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class RiskScoringEngine:
    """
    Analyzes system metrics and generates risk scores with root cause analysis
    """
    
    def __init__(self):
        self.risk_thresholds = {
            'accuracy': {'critical': 0.85, 'warning': 0.90},
            'latency_ms': {'critical': 200, 'warning': 100},
            'error_rate': {'critical': 0.05, 'warning': 0.02},
            'cpu_utilization': {'critical': 85, 'warning': 70},
            'memory_utilization': {'critical': 85, 'warning': 70},
            'data_drift_score': {'critical': 0.5, 'warning': 0.3},
            'cost_per_hour': {'critical': 50, 'warning': 30}
        }
    
    def calculate_health_score(self, metrics: Dict) -> float:
        """
        Calculate overall system health score (0-100)
        """
        scores = []
        
        # Accuracy contribution (25%)
        if 'accuracy' in metrics:
            accuracy_score = metrics['accuracy'] * 100
            scores.append(('accuracy', accuracy_score, 0.25))
        
        # Latency contribution (20%)
        if 'latency_ms' in metrics:
            latency_score = max(0, 100 - (metrics['latency_ms'] - 50) / 2)
            scores.append(('latency', latency_score, 0.20))
        
        # Error rate contribution (20%)
        if 'error_rate' in metrics:
            error_score = max(0, 100 - metrics['error_rate'] * 1000)
            scores.append(('error_rate', error_score, 0.20))
        
        # Resource utilization contribution (15%)
        if 'cpu_utilization' in metrics and 'memory_utilization' in metrics:
            resource_score = 100 - (metrics['cpu_utilization'] + metrics['memory_utilization']) / 2
            scores.append(('resources', max(0, resource_score), 0.15))
        
        # Data quality contribution (10%)
        if 'data_drift_score' in metrics:
            drift_score = max(0, 100 - metrics['data_drift_score'] * 100)
            scores.append(('data_quality', drift_score, 0.10))
        
        # Pipeline reliability contribution (10%)
        if 'pipeline_success_rate' in metrics:
            pipeline_score = metrics['pipeline_success_rate'] * 100
            scores.append(('pipeline', pipeline_score, 0.10))
        
        # Calculate weighted average
        if not scores:
            return 50.0
        
        total_weight = sum(weight for _, _, weight in scores)
        weighted_sum = sum(score * weight for _, score, weight in scores)
        
        health_score = weighted_sum / total_weight
        return round(np.clip(health_score, 0, 100), 2)
    
    def calculate_failure_probability(self, 
                                     prediction_score: float,
                                     current_metrics: Dict,
                                     historical_trend: str = 'stable') -> Dict:
        """
        Calculate probability of failure in next 24-72 hours
        """
        # Base probability from model prediction
        base_prob = prediction_score
        
        # Adjust based on current metrics
        adjustments = []
        
        # Check if metrics are in critical zones
        if current_metrics.get('accuracy', 1.0) < self.risk_thresholds['accuracy']['critical']:
            adjustments.append(0.15)
        
        if current_metrics.get('latency_ms', 0) > self.risk_thresholds['latency_ms']['critical']:
            adjustments.append(0.10)
        
        if current_metrics.get('error_rate', 0) > self.risk_thresholds['error_rate']['critical']:
            adjustments.append(0.15)
        
        if current_metrics.get('data_drift_score', 0) > self.risk_thresholds['data_drift_score']['critical']:
            adjustments.append(0.10)
        
        # Trend adjustment
        trend_multiplier = {
            'improving': 0.8,
            'stable': 1.0,
            'degrading': 1.3,
            'critical': 1.5
        }
        
        adjusted_prob = base_prob * trend_multiplier.get(historical_trend, 1.0)
        adjusted_prob += sum(adjustments)
        adjusted_prob = np.clip(adjusted_prob, 0, 1)
        
        # Time-based breakdown
        prob_24h = adjusted_prob * 0.4
        prob_48h = adjusted_prob * 0.7
        prob_72h = adjusted_prob
        
        return {
            'overall': round(adjusted_prob * 100, 2),
            '24h': round(prob_24h * 100, 2),
            '48h': round(prob_48h * 100, 2),
            '72h': round(prob_72h * 100, 2),
            'confidence': self._calculate_confidence(current_metrics)
        }
    
    def _calculate_confidence(self, metrics: Dict) -> float:
        """
        Calculate confidence in the prediction
        """
        # More complete metrics = higher confidence
        expected_metrics = ['accuracy', 'latency_ms', 'error_rate', 'cpu_utilization', 
                          'memory_utilization', 'data_drift_score']
        
        present_metrics = sum(1 for m in expected_metrics if m in metrics)
        completeness = present_metrics / len(expected_metrics)
        
        # Check data quality
        data_quality = 1.0
        if 'data_drift_score' in metrics:
            data_quality = 1 - min(metrics['data_drift_score'], 1.0)
        
        confidence = (completeness * 0.7 + data_quality * 0.3) * 100
        return round(confidence, 2)
    
    def identify_root_causes(self, metrics: Dict, historical_data: pd.DataFrame = None) -> List[Dict]:
        """
        Identify potential root causes of issues
        """
        root_causes = []
        
        # Check accuracy degradation
        if metrics.get('accuracy', 1.0) < self.risk_thresholds['accuracy']['warning']:
            severity = 'critical' if metrics['accuracy'] < self.risk_thresholds['accuracy']['critical'] else 'warning'
            cause = {
                'category': 'Model Performance',
                'issue': 'Accuracy Degradation',
                'severity': severity,
                'current_value': f"{metrics['accuracy']:.3f}",
                'threshold': f"{self.risk_thresholds['accuracy'][severity]}",
                'impact': 'High',
                'description': 'Model accuracy has fallen below acceptable thresholds'
            }
            root_causes.append(cause)
        
        # Check latency spikes
        if metrics.get('latency_ms', 0) > self.risk_thresholds['latency_ms']['warning']:
            severity = 'critical' if metrics['latency_ms'] > self.risk_thresholds['latency_ms']['critical'] else 'warning'
            cause = {
                'category': 'Performance',
                'issue': 'High Latency',
                'severity': severity,
                'current_value': f"{metrics['latency_ms']:.1f}ms",
                'threshold': f"{self.risk_thresholds['latency_ms'][severity]}ms",
                'impact': 'High',
                'description': 'Response time exceeds acceptable limits'
            }
            root_causes.append(cause)
        
        # Check error rates
        if metrics.get('error_rate', 0) > self.risk_thresholds['error_rate']['warning']:
            severity = 'critical' if metrics['error_rate'] > self.risk_thresholds['error_rate']['critical'] else 'warning'
            cause = {
                'category': 'Reliability',
                'issue': 'Elevated Error Rate',
                'severity': severity,
                'current_value': f"{metrics['error_rate']*100:.2f}%",
                'threshold': f"{self.risk_thresholds['error_rate'][severity]*100:.2f}%",
                'impact': 'High',
                'description': 'System error rate is abnormally high'
            }
            root_causes.append(cause)
        
        # Check resource exhaustion
        cpu = metrics.get('cpu_utilization', 0)
        memory = metrics.get('memory_utilization', 0)
        
        if cpu > self.risk_thresholds['cpu_utilization']['warning']:
            severity = 'critical' if cpu > self.risk_thresholds['cpu_utilization']['critical'] else 'warning'
            cause = {
                'category': 'Infrastructure',
                'issue': 'High CPU Utilization',
                'severity': severity,
                'current_value': f"{cpu:.1f}%",
                'threshold': f"{self.risk_thresholds['cpu_utilization'][severity]}%",
                'impact': 'Medium',
                'description': 'CPU usage approaching capacity limits'
            }
            root_causes.append(cause)
        
        if memory > self.risk_thresholds['memory_utilization']['warning']:
            severity = 'critical' if memory > self.risk_thresholds['memory_utilization']['critical'] else 'warning'
            cause = {
                'category': 'Infrastructure',
                'issue': 'High Memory Utilization',
                'severity': severity,
                'current_value': f"{memory:.1f}%",
                'threshold': f"{self.risk_thresholds['memory_utilization'][severity]}%",
                'impact': 'Medium',
                'description': 'Memory usage may lead to OOM errors'
            }
            root_causes.append(cause)
        
        # Check data drift
        if metrics.get('data_drift_score', 0) > self.risk_thresholds['data_drift_score']['warning']:
            severity = 'critical' if metrics['data_drift_score'] > self.risk_thresholds['data_drift_score']['critical'] else 'warning'
            cause = {
                'category': 'Data Quality',
                'issue': 'Data Distribution Drift',
                'severity': severity,
                'current_value': f"{metrics['data_drift_score']:.3f}",
                'threshold': f"{self.risk_thresholds['data_drift_score'][severity]}",
                'impact': 'High',
                'description': 'Input data distribution has shifted significantly'
            }
            root_causes.append(cause)
        
        # Check cost overrun
        if metrics.get('cost_per_hour', 0) > self.risk_thresholds['cost_per_hour']['warning']:
            severity = 'critical' if metrics['cost_per_hour'] > self.risk_thresholds['cost_per_hour']['critical'] else 'warning'
            cause = {
                'category': 'Cost',
                'issue': 'Cost Overrun',
                'severity': severity,
                'current_value': f"${metrics['cost_per_hour']:.2f}/hr",
                'threshold': f"${self.risk_thresholds['cost_per_hour'][severity]}/hr",
                'impact': 'Medium',
                'description': 'Infrastructure costs exceeding budget'
            }
            root_causes.append(cause)
        
        # Sort by severity
        severity_order = {'critical': 0, 'warning': 1}
        root_causes.sort(key=lambda x: severity_order.get(x['severity'], 2))
        
        return root_causes
    
    def generate_risk_report(self, 
                           current_metrics: Dict,
                           prediction_score: float,
                           historical_data: pd.DataFrame = None) -> Dict:
        """
        Generate comprehensive risk report
        """
        health_score = self.calculate_health_score(current_metrics)
        
        # Determine trend
        trend = 'stable'
        if historical_data is not None and len(historical_data) > 24:
            recent_health = [self.calculate_health_score(row.to_dict()) 
                           for _, row in historical_data.tail(24).iterrows()]
            if len(recent_health) >= 24:
                if recent_health[-1] < recent_health[0] - 10:
                    trend = 'degrading' if recent_health[-1] > 50 else 'critical'
                elif recent_health[-1] > recent_health[0] + 10:
                    trend = 'improving'
        
        failure_prob = self.calculate_failure_probability(
            prediction_score, current_metrics, trend
        )
        
        root_causes = self.identify_root_causes(current_metrics, historical_data)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'trend': trend,
            'failure_probability': failure_prob,
            'root_causes': root_causes,
            'metrics_snapshot': current_metrics
        }
