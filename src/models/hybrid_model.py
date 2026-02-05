"""
Hybrid LSTM + XGBoost Model for Failure Prediction
Combines temporal pattern recognition with gradient boosting
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional
import pickle
import os

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


class HybridFailurePredictionModel:
    """
    Hybrid model combining LSTM for temporal patterns and XGBoost for feature interactions
    """
    
    def __init__(self, 
                 sequence_length: int = 24,
                 lstm_units: int = 128,
                 dropout_rate: float = 0.3):
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        
        self.lstm_model = None
        self.xgb_model = None
        self.feature_names = []
        
    def create_sequences(self, data: np.ndarray, labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM input
        """
        X_seq = []
        y_seq = []
        
        for i in range(len(data) - self.sequence_length):
            X_seq.append(data[i:i + self.sequence_length])
            y_seq.append(labels[i + self.sequence_length])
        
        return np.array(X_seq), np.array(y_seq)
    
    def build_lstm_model(self, input_shape: Tuple) -> Optional[Model]:
        """
        Build LSTM model for temporal pattern recognition
        """
        if not TENSORFLOW_AVAILABLE:
            print("TensorFlow not available. LSTM model will not be used.")
            return None
            
        model = Sequential([
            LSTM(self.lstm_units, return_sequences=True, input_shape=input_shape),
            Dropout(self.dropout_rate),
            LSTM(self.lstm_units // 2, return_sequences=False),
            Dropout(self.dropout_rate),
            Dense(64, activation='relu'),
            Dropout(self.dropout_rate),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        return model
    
    def train_lstm(self, X: np.ndarray, y: np.ndarray, 
                   validation_split: float = 0.2,
                   epochs: int = 50,
                   batch_size: int = 32) -> Dict:
        """
        Train LSTM model
        """
        if not TENSORFLOW_AVAILABLE:
            return {'status': 'skipped', 'reason': 'TensorFlow not available'}
        
        # Create sequences
        X_seq, y_seq = self.create_sequences(X, y)
        
        # Build model
        self.lstm_model = self.build_lstm_model((self.sequence_length, X.shape[1]))
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train
        history = self.lstm_model.fit(
            X_seq, y_seq,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping],
            verbose=0
        )
        
        return {
            'status': 'success',
            'history': history.history,
            'final_loss': history.history['loss'][-1],
            'final_val_loss': history.history['val_loss'][-1]
        }
    
    def train_xgboost(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Train XGBoost model
        """
        if not XGBOOST_AVAILABLE:
            return {'status': 'skipped', 'reason': 'XGBoost not available'}
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # XGBoost parameters tuned for imbalanced failure prediction
        params = {
            'objective': 'binary:logistic',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'scale_pos_weight': len(y_train[y_train == 0]) / len(y_train[y_train == 1]),
            'eval_metric': 'auc',
            'random_state': 42
        }
        
        self.xgb_model = xgb.XGBClassifier(**params)
        
        self.xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=20,
            verbose=False
        )
        
        # Evaluate
        y_pred = self.xgb_model.predict(X_val)
        y_pred_proba = self.xgb_model.predict_proba(X_val)[:, 1]
        
        metrics = {
            'status': 'success',
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred, zero_division=0),
            'recall': recall_score(y_val, y_pred, zero_division=0),
            'f1': f1_score(y_val, y_pred, zero_division=0),
            'auc': roc_auc_score(y_val, y_pred_proba)
        }
        
        return metrics
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Train both LSTM and XGBoost models
        """
        self.feature_names = X.columns.tolist()
        X_array = X.values
        y_array = y.values
        
        results = {}
        
        # Train LSTM for temporal patterns
        print("Training LSTM model...")
        lstm_results = self.train_lstm(X_array, y_array)
        results['lstm'] = lstm_results
        
        # Train XGBoost for feature interactions
        print("Training XGBoost model...")
        xgb_results = self.train_xgboost(X_array, y_array)
        results['xgboost'] = xgb_results
        
        return results
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Make hybrid predictions combining LSTM and XGBoost
        Returns: ensemble predictions, lstm predictions, xgb predictions
        """
        lstm_pred = np.zeros(len(X))
        xgb_pred = np.zeros(len(X))
        
        # LSTM predictions
        if self.lstm_model is not None and TENSORFLOW_AVAILABLE:
            X_seq, _ = self.create_sequences(X, np.zeros(len(X)))
            lstm_pred_seq = self.lstm_model.predict(X_seq, verbose=0).flatten()
            # Pad beginning with zeros
            lstm_pred[self.sequence_length:] = lstm_pred_seq
        
        # XGBoost predictions
        if self.xgb_model is not None and XGBOOST_AVAILABLE:
            xgb_pred = self.xgb_model.predict_proba(X)[:, 1]
        
        # Ensemble: weighted average (0.6 LSTM, 0.4 XGBoost)
        # LSTM better for temporal patterns, XGBoost for feature interactions
        ensemble_pred = 0.6 * lstm_pred + 0.4 * xgb_pred
        
        return ensemble_pred, lstm_pred, xgb_pred
    
    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Get feature importance from XGBoost model
        """
        if self.xgb_model is None or not XGBOOST_AVAILABLE:
            return None
        
        importance = self.xgb_model.feature_importances_
        
        df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        })
        
        return df.sort_values('importance', ascending=False)
    
    def save_models(self, directory: str):
        """
        Save trained models
        """
        os.makedirs(directory, exist_ok=True)
        
        if self.lstm_model is not None and TENSORFLOW_AVAILABLE:
            self.lstm_model.save(os.path.join(directory, 'lstm_model.h5'))
        
        if self.xgb_model is not None and XGBOOST_AVAILABLE:
            with open(os.path.join(directory, 'xgb_model.pkl'), 'wb') as f:
                pickle.dump(self.xgb_model, f)
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'sequence_length': self.sequence_length,
            'lstm_units': self.lstm_units,
            'dropout_rate': self.dropout_rate
        }
        
        with open(os.path.join(directory, 'metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)
    
    def load_models(self, directory: str):
        """
        Load trained models
        """
        # Load metadata
        with open(os.path.join(directory, 'metadata.pkl'), 'rb') as f:
            metadata = pickle.load(f)
        
        self.feature_names = metadata['feature_names']
        self.sequence_length = metadata['sequence_length']
        self.lstm_units = metadata['lstm_units']
        self.dropout_rate = metadata['dropout_rate']
        
        # Load LSTM
        lstm_path = os.path.join(directory, 'lstm_model.h5')
        if os.path.exists(lstm_path) and TENSORFLOW_AVAILABLE:
            self.lstm_model = keras.models.load_model(lstm_path)
        
        # Load XGBoost
        xgb_path = os.path.join(directory, 'xgb_model.pkl')
        if os.path.exists(xgb_path) and XGBOOST_AVAILABLE:
            with open(xgb_path, 'rb') as f:
                self.xgb_model = pickle.load(f)
