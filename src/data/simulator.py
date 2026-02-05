"""
Data Simulator for ML System Metrics
Generates realistic logs, metrics, drift, latency, and cost data
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random


class MLSystemDataSimulator:
    """
    Simulates ML system operational data for failure prediction
    """
    
    def __init__(self, days_history: int = 90):
        self.days_history = days_history
        self.base_timestamp = datetime.now() - timedelta(days=days_history)
        
    def generate_metrics_data(self) -> pd.DataFrame:
        """
        Generate time-series metrics data for ML system
        Returns DataFrame with realistic operational metrics
        """
        hours = self.days_history * 24
        timestamps = [self.base_timestamp + timedelta(hours=i) for i in range(hours)]
        
        # Base patterns
        t = np.arange(hours)
        
        # Model accuracy with gradual degradation and sudden drops
        base_accuracy = 0.95
        drift_effect = -0.0001 * t  # Gradual drift
        seasonal = 0.02 * np.sin(2 * np.pi * t / (24 * 7))  # Weekly pattern
        random_noise = np.random.normal(0, 0.01, hours)
        
        # Add failure events (sudden drops)
        failure_points = random.sample(range(hours), k=max(1, hours // 500))
        failure_effect = np.zeros(hours)
        for fp in failure_points:
            failure_effect[fp:min(fp+24, hours)] = -0.1  # 24-hour degradation
        
        accuracy = base_accuracy + drift_effect + seasonal + random_noise + failure_effect
        accuracy = np.clip(accuracy, 0.5, 1.0)
        
        # Latency with spikes
        base_latency = 50  # ms
        traffic_pattern = 20 * (np.sin(2 * np.pi * t / 24) + 1)  # Daily pattern
        latency_noise = np.random.exponential(10, hours)
        
        # Latency spikes
        spike_points = random.sample(range(hours), k=max(1, hours // 300))
        spike_effect = np.zeros(hours)
        for sp in spike_points:
            spike_effect[sp:min(sp+6, hours)] = 200  # 6-hour spike
        
        latency = base_latency + traffic_pattern + latency_noise + spike_effect
        latency = np.clip(latency, 10, 500)
        
        # Request volume
        base_volume = 10000
        volume = base_volume + 5000 * (np.sin(2 * np.pi * t / 24) + 1)
        volume += np.random.normal(0, 1000, hours)
        volume = np.clip(volume, 1000, 30000).astype(int)
        
        # Error rate
        base_error_rate = 0.01
        error_rate = base_error_rate + 0.005 * (1 - accuracy / 0.95)
        error_rate += np.random.exponential(0.005, hours)
        error_rate = np.clip(error_rate, 0, 0.5)
        
        # CPU utilization
        base_cpu = 45
        cpu = base_cpu + 30 * (np.sin(2 * np.pi * t / 24) + 1)
        cpu += np.random.normal(0, 5, hours)
        cpu = np.clip(cpu, 10, 100)
        
        # Memory utilization
        base_memory = 60
        memory_leak = 0.01 * t  # Gradual increase
        memory = base_memory + memory_leak + np.random.normal(0, 3, hours)
        memory = np.clip(memory, 20, 95)
        
        # Cost per hour
        base_cost = 10
        cost = base_cost * (cpu / 50) * (volume / 10000)
        cost += np.random.normal(0, 2, hours)
        cost = np.clip(cost, 1, 100)
        
        # Data drift score (0-1, higher = more drift)
        base_drift = 0.1
        drift_accumulation = 0.0005 * t
        drift = base_drift + drift_accumulation + np.random.normal(0, 0.05, hours)
        drift = np.clip(drift, 0, 1)
        
        # Pipeline success rate
        pipeline_success = 0.98 - 0.1 * (error_rate / 0.05)
        pipeline_success += np.random.normal(0, 0.02, hours)
        pipeline_success = np.clip(pipeline_success, 0.5, 1.0)
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'accuracy': accuracy,
            'latency_ms': latency,
            'request_volume': volume,
            'error_rate': error_rate,
            'cpu_utilization': cpu,
            'memory_utilization': memory,
            'cost_per_hour': cost,
            'data_drift_score': drift,
            'pipeline_success_rate': pipeline_success
        })
        
        return df
    
    def generate_logs(self, n_logs: int = 1000) -> pd.DataFrame:
        """
        Generate synthetic log data
        """
        log_levels = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
        log_sources = ['MODEL_INFERENCE', 'DATA_PIPELINE', 'API_GATEWAY', 'DATABASE', 'CACHE']
        
        logs = []
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(n_logs):
            timestamp = base_time + timedelta(seconds=random.randint(0, 86400))
            level = random.choices(log_levels, weights=[70, 20, 8, 2])[0]
            source = random.choice(log_sources)
            
            # Generate realistic log messages
            if level == 'ERROR':
                messages = [
                    f"Timeout connecting to {source}",
                    f"Failed to process request in {source}",
                    f"High latency detected in {source}",
                    f"Resource exhaustion in {source}"
                ]
            elif level == 'WARNING':
                messages = [
                    f"High memory usage in {source}",
                    f"Slow query detected in {source}",
                    f"Retry attempt {random.randint(1,3)} for {source}",
                    f"Cache miss rate elevated in {source}"
                ]
            else:
                messages = [
                    f"Request processed successfully in {source}",
                    f"Health check passed for {source}",
                    f"Batch job completed in {source}"
                ]
            
            logs.append({
                'timestamp': timestamp,
                'level': level,
                'source': source,
                'message': random.choice(messages)
            })
        
        return pd.DataFrame(logs).sort_values('timestamp')
    
    def inject_failure_scenario(self, df: pd.DataFrame, 
                               start_idx: int, duration_hours: int = 48) -> pd.DataFrame:
        """
        Inject a failure scenario into the data
        """
        df_copy = df.copy()
        end_idx = min(start_idx + duration_hours, len(df))
        
        # Gradual degradation leading to failure
        for i in range(start_idx, end_idx):
            progress = (i - start_idx) / duration_hours
            
            # Accuracy decay
            df_copy.loc[i, 'accuracy'] *= (1 - 0.3 * progress)
            
            # Latency spike
            df_copy.loc[i, 'latency_ms'] *= (1 + 2 * progress)
            
            # Error rate increase
            df_copy.loc[i, 'error_rate'] *= (1 + 5 * progress)
            
            # Resource exhaustion
            df_copy.loc[i, 'cpu_utilization'] = min(95, df_copy.loc[i, 'cpu_utilization'] * (1 + progress))
            df_copy.loc[i, 'memory_utilization'] = min(95, df_copy.loc[i, 'memory_utilization'] * (1 + progress))
            
            # Cost spike
            df_copy.loc[i, 'cost_per_hour'] *= (1 + 1.5 * progress)
            
            # Data drift
            df_copy.loc[i, 'data_drift_score'] = min(0.9, df_copy.loc[i, 'data_drift_score'] * (1 + 2 * progress))
        
        return df_copy
    
    def get_labeled_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Generate labeled data for training
        Returns features and failure labels (1 = failure within 48h, 0 = normal)
        """
        df = self.generate_metrics_data()
        
        # Create failure labels (look ahead 48 hours)
        window = 48
        labels = pd.Series(0, index=df.index)
        
        # Detect failures (significant accuracy drop or latency spike)
        for i in range(len(df) - window):
            future_window = df.iloc[i:i+window]
            
            accuracy_drop = (df.iloc[i]['accuracy'] - future_window['accuracy'].min()) > 0.1
            latency_spike = (future_window['latency_ms'].max() - df.iloc[i]['latency_ms']) > 100
            error_spike = (future_window['error_rate'].max() - df.iloc[i]['error_rate']) > 0.05
            
            if accuracy_drop or latency_spike or error_spike:
                labels.iloc[i] = 1
        
        return df, labels
