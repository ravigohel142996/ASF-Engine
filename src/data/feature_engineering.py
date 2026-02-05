"""
Feature Engineering for ML System Monitoring
Extracts and creates predictive features from raw metrics
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.preprocessing import StandardScaler


class FeatureEngineer:
    """
    Transforms raw metrics into predictive features
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract temporal features from timestamp
        """
        df = df.copy()
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_business_hours'] = df['hour'].between(9, 17).astype(int)
        
        # Cyclical encoding for hour and day
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, windows: List[int] = [6, 12, 24]) -> pd.DataFrame:
        """
        Create rolling statistics for time-series features
        """
        df = df.copy()
        
        metric_columns = [
            'accuracy', 'latency_ms', 'error_rate', 
            'cpu_utilization', 'memory_utilization', 
            'cost_per_hour', 'data_drift_score'
        ]
        
        for window in windows:
            for col in metric_columns:
                if col in df.columns:
                    # Rolling statistics
                    df[f'{col}_rolling_mean_{window}h'] = df[col].rolling(window=window, min_periods=1).mean()
                    df[f'{col}_rolling_std_{window}h'] = df[col].rolling(window=window, min_periods=1).std()
                    df[f'{col}_rolling_min_{window}h'] = df[col].rolling(window=window, min_periods=1).min()
                    df[f'{col}_rolling_max_{window}h'] = df[col].rolling(window=window, min_periods=1).max()
        
        return df
    
    def create_trend_features(self, df: pd.DataFrame, windows: List[int] = [12, 24, 48]) -> pd.DataFrame:
        """
        Calculate trend and rate of change features
        """
        df = df.copy()
        
        metric_columns = [
            'accuracy', 'latency_ms', 'error_rate',
            'cpu_utilization', 'memory_utilization'
        ]
        
        for window in windows:
            for col in metric_columns:
                if col in df.columns:
                    # Rate of change
                    df[f'{col}_change_{window}h'] = df[col].diff(window)
                    
                    # Percentage change
                    df[f'{col}_pct_change_{window}h'] = df[col].pct_change(window)
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features between metrics
        """
        df = df.copy()
        
        # Performance indicators
        if 'latency_ms' in df.columns and 'request_volume' in df.columns:
            df['throughput'] = df['request_volume'] / (df['latency_ms'] + 1)
        
        # Resource efficiency
        if 'cpu_utilization' in df.columns and 'request_volume' in df.columns:
            df['cpu_per_request'] = df['cpu_utilization'] / (df['request_volume'] + 1)
        
        if 'memory_utilization' in df.columns and 'request_volume' in df.columns:
            df['memory_per_request'] = df['memory_utilization'] / (df['request_volume'] + 1)
        
        # Cost efficiency
        if 'cost_per_hour' in df.columns and 'request_volume' in df.columns:
            df['cost_per_request'] = df['cost_per_hour'] / (df['request_volume'] + 1)
        
        # Quality metrics
        if 'accuracy' in df.columns and 'data_drift_score' in df.columns:
            df['accuracy_drift_interaction'] = df['accuracy'] * (1 - df['data_drift_score'])
        
        # System stress indicator
        if 'cpu_utilization' in df.columns and 'memory_utilization' in df.columns:
            df['system_stress'] = (df['cpu_utilization'] + df['memory_utilization']) / 2
        
        # Error density
        if 'error_rate' in df.columns and 'request_volume' in df.columns:
            df['error_count'] = df['error_rate'] * df['request_volume']
        
        return df
    
    def create_anomaly_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate statistical anomaly scores
        """
        df = df.copy()
        
        metric_columns = [
            'accuracy', 'latency_ms', 'error_rate',
            'cpu_utilization', 'memory_utilization'
        ]
        
        for col in metric_columns:
            if col in df.columns:
                mean = df[col].rolling(window=24*7, min_periods=1).mean()
                std = df[col].rolling(window=24*7, min_periods=1).std()
                
                # Z-score based anomaly detection
                df[f'{col}_zscore'] = (df[col] - mean) / (std + 1e-6)
                df[f'{col}_is_anomaly'] = (np.abs(df[f'{col}_zscore']) > 3).astype(int)
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering transformations
        """
        df = self.create_time_features(df)
        df = self.create_rolling_features(df)
        df = self.create_trend_features(df)
        df = self.create_interaction_features(df)
        df = self.create_anomaly_scores(df)
        
        # Fill NaN values created by rolling operations
        df = df.fillna(method='bfill').fillna(0)
        
        return df
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of feature columns (exclude timestamp and identifiers)
        """
        exclude_cols = ['timestamp']
        return [col for col in df.columns if col not in exclude_cols]
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit scaler and transform features
        """
        feature_cols = self.get_feature_columns(df)
        self.feature_names = feature_cols
        
        df_scaled = df.copy()
        df_scaled[feature_cols] = self.scaler.fit_transform(df[feature_cols])
        
        return df_scaled
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform features using fitted scaler
        """
        feature_cols = self.get_feature_columns(df)
        
        df_scaled = df.copy()
        df_scaled[feature_cols] = self.scaler.transform(df[feature_cols])
        
        return df_scaled
