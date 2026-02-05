"""
Alert Generation System
Generates alerts and recommendations for system issues
"""
from typing import Dict, List
from datetime import datetime
import uuid


class AlertGenerator:
    """
    Generates and manages alerts for system failures and issues
    """
    
    def __init__(self):
        self.alert_history = []
        self.active_alerts = []
        
    def create_alert(self, 
                    alert_type: str,
                    severity: str,
                    title: str,
                    description: str,
                    metrics: Dict = None,
                    recommendations: List[str] = None) -> Dict:
        """
        Create a new alert
        """
        alert = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'severity': severity,
            'title': title,
            'description': description,
            'metrics': metrics or {},
            'recommendations': recommendations or [],
            'status': 'active',
            'acknowledged': False
        }
        
        self.alert_history.append(alert)
        self.active_alerts.append(alert)
        
        return alert
    
    def generate_alerts_from_risk_report(self, risk_report: Dict) -> List[Dict]:
        """
        Generate alerts based on risk report
        """
        alerts = []
        
        # High failure probability alert
        if risk_report['failure_probability']['overall'] > 70:
            alert = self.create_alert(
                alert_type='FAILURE_PREDICTION',
                severity='critical',
                title='Critical: High Failure Probability Detected',
                description=f"System has {risk_report['failure_probability']['overall']}% probability of failure in next 72 hours",
                metrics={'failure_probability': risk_report['failure_probability']},
                recommendations=self._get_failure_recommendations(risk_report)
            )
            alerts.append(alert)
        elif risk_report['failure_probability']['overall'] > 40:
            alert = self.create_alert(
                alert_type='FAILURE_PREDICTION',
                severity='warning',
                title='Warning: Elevated Failure Risk',
                description=f"System has {risk_report['failure_probability']['overall']}% probability of failure in next 72 hours",
                metrics={'failure_probability': risk_report['failure_probability']},
                recommendations=self._get_failure_recommendations(risk_report)
            )
            alerts.append(alert)
        
        # Low health score alert
        if risk_report['health_score'] < 50:
            alert = self.create_alert(
                alert_type='HEALTH_DEGRADATION',
                severity='critical',
                title='Critical: System Health Severely Degraded',
                description=f"Overall health score: {risk_report['health_score']}/100",
                metrics={'health_score': risk_report['health_score']},
                recommendations=['Immediate investigation required', 'Consider rollback to last stable version']
            )
            alerts.append(alert)
        elif risk_report['health_score'] < 70:
            alert = self.create_alert(
                alert_type='HEALTH_DEGRADATION',
                severity='warning',
                title='Warning: System Health Declining',
                description=f"Overall health score: {risk_report['health_score']}/100",
                metrics={'health_score': risk_report['health_score']},
                recommendations=['Monitor closely', 'Review recent changes']
            )
            alerts.append(alert)
        
        # Root cause specific alerts
        for cause in risk_report['root_causes']:
            if cause['severity'] == 'critical':
                alert = self.create_alert(
                    alert_type=cause['category'].upper().replace(' ', '_'),
                    severity='critical',
                    title=f"Critical: {cause['issue']}",
                    description=cause['description'],
                    metrics={
                        'current_value': cause['current_value'],
                        'threshold': cause['threshold']
                    },
                    recommendations=self._get_cause_specific_recommendations(cause)
                )
                alerts.append(alert)
        
        return alerts
    
    def _get_failure_recommendations(self, risk_report: Dict) -> List[str]:
        """
        Get recommendations based on failure risk
        """
        recommendations = []
        
        # Based on root causes
        root_causes = risk_report.get('root_causes', [])
        
        for cause in root_causes:
            if cause['category'] == 'Model Performance':
                recommendations.extend([
                    'Retrain model with recent data',
                    'Enable shadow deployment for new model',
                    'Increase model validation frequency'
                ])
            elif cause['category'] == 'Performance':
                recommendations.extend([
                    'Scale up infrastructure',
                    'Enable caching layer',
                    'Optimize query performance'
                ])
            elif cause['category'] == 'Data Quality':
                recommendations.extend([
                    'Review data pipeline for anomalies',
                    'Implement stricter input validation',
                    'Update feature transformations'
                ])
            elif cause['category'] == 'Infrastructure':
                recommendations.extend([
                    'Horizontal scaling needed',
                    'Check for resource leaks',
                    'Review auto-scaling policies'
                ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:5]  # Top 5 recommendations
    
    def _get_cause_specific_recommendations(self, cause: Dict) -> List[str]:
        """
        Get specific recommendations for a root cause
        """
        recommendations_map = {
            'Accuracy Degradation': [
                'Retrain model immediately',
                'Check for data distribution changes',
                'Review feature importance shifts',
                'Enable A/B testing with previous model version'
            ],
            'High Latency': [
                'Scale compute resources',
                'Enable request batching',
                'Optimize model inference',
                'Implement response caching'
            ],
            'Elevated Error Rate': [
                'Review recent deployments',
                'Check dependency health',
                'Increase retry policies',
                'Enable circuit breakers'
            ],
            'High CPU Utilization': [
                'Scale out worker instances',
                'Optimize compute-intensive operations',
                'Enable auto-scaling',
                'Review CPU profiling data'
            ],
            'High Memory Utilization': [
                'Check for memory leaks',
                'Optimize data structures',
                'Increase memory limits',
                'Enable memory profiling'
            ],
            'Data Distribution Drift': [
                'Retrain model on recent data',
                'Update feature normalization',
                'Review data sources',
                'Implement drift detection alerts'
            ],
            'Cost Overrun': [
                'Review resource utilization',
                'Optimize instance types',
                'Enable cost anomaly detection',
                'Implement resource quotas'
            ]
        }
        
        return recommendations_map.get(cause['issue'], ['Investigate and resolve issue'])
    
    def get_active_alerts(self, severity: str = None) -> List[Dict]:
        """
        Get active alerts, optionally filtered by severity
        """
        if severity:
            return [a for a in self.active_alerts if a['severity'] == severity]
        return self.active_alerts
    
    def get_alert_summary(self) -> Dict:
        """
        Get summary of all alerts
        """
        critical = len([a for a in self.active_alerts if a['severity'] == 'critical'])
        warning = len([a for a in self.active_alerts if a['severity'] == 'warning'])
        info = len([a for a in self.active_alerts if a['severity'] == 'info'])
        
        return {
            'total_active': len(self.active_alerts),
            'critical': critical,
            'warning': warning,
            'info': info,
            'total_historical': len(self.alert_history)
        }


class RecommendationEngine:
    """
    Provides actionable recommendations for system issues
    """
    
    def generate_mitigation_plan(self, risk_report: Dict) -> Dict:
        """
        Generate comprehensive mitigation plan
        """
        root_causes = risk_report.get('root_causes', [])
        
        immediate_actions = []
        short_term_actions = []
        long_term_actions = []
        
        # Immediate actions (next 1-4 hours)
        if risk_report['failure_probability']['24h'] > 50:
            immediate_actions.extend([
                'Activate incident response team',
                'Prepare rollback procedures',
                'Enable enhanced monitoring',
                'Notify stakeholders of elevated risk'
            ])
        
        # Analyze root causes for specific actions
        has_model_issues = any(c['category'] == 'Model Performance' for c in root_causes)
        has_infra_issues = any(c['category'] == 'Infrastructure' for c in root_causes)
        has_data_issues = any(c['category'] == 'Data Quality' for c in root_causes)
        
        if has_model_issues:
            immediate_actions.append('Switch to backup model if available')
            short_term_actions.extend([
                'Initiate model retraining pipeline',
                'Analyze model performance degradation',
                'Review recent data quality issues'
            ])
            long_term_actions.extend([
                'Implement continuous model monitoring',
                'Set up automated retraining pipeline',
                'Establish model performance SLAs'
            ])
        
        if has_infra_issues:
            immediate_actions.append('Scale up critical resources')
            short_term_actions.extend([
                'Review resource allocation',
                'Optimize infrastructure configuration',
                'Check for resource leaks'
            ])
            long_term_actions.extend([
                'Implement auto-scaling policies',
                'Review capacity planning',
                'Optimize resource efficiency'
            ])
        
        if has_data_issues:
            immediate_actions.append('Enable data quality checks')
            short_term_actions.extend([
                'Investigate data source changes',
                'Review ETL pipeline health',
                'Validate data transformations'
            ])
            long_term_actions.extend([
                'Implement automated data validation',
                'Set up data drift monitoring',
                'Establish data quality SLAs'
            ])
        
        return {
            'risk_level': self._get_risk_level(risk_report),
            'immediate_actions': immediate_actions[:5],
            'short_term_actions': short_term_actions[:5],
            'long_term_actions': long_term_actions[:5],
            'estimated_mttr': self._estimate_mttr(risk_report),
            'priority': self._calculate_priority(risk_report)
        }
    
    def _get_risk_level(self, risk_report: Dict) -> str:
        """
        Determine overall risk level
        """
        failure_prob = risk_report['failure_probability']['overall']
        health_score = risk_report['health_score']
        
        if failure_prob > 70 or health_score < 50:
            return 'CRITICAL'
        elif failure_prob > 40 or health_score < 70:
            return 'HIGH'
        elif failure_prob > 20 or health_score < 85:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _estimate_mttr(self, risk_report: Dict) -> str:
        """
        Estimate Mean Time To Recovery
        """
        root_causes = risk_report.get('root_causes', [])
        critical_count = sum(1 for c in root_causes if c['severity'] == 'critical')
        
        if critical_count >= 3:
            return '4-8 hours'
        elif critical_count >= 1:
            return '2-4 hours'
        else:
            return '1-2 hours'
    
    def _calculate_priority(self, risk_report: Dict) -> str:
        """
        Calculate incident priority
        """
        failure_prob = risk_report['failure_probability']['overall']
        health_score = risk_report['health_score']
        
        if failure_prob > 70 and health_score < 50:
            return 'P0 - Critical'
        elif failure_prob > 50 or health_score < 60:
            return 'P1 - High'
        elif failure_prob > 30 or health_score < 75:
            return 'P2 - Medium'
        else:
            return 'P3 - Low'
