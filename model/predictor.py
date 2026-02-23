"""
Water Quality Prediction Model using Scikit-Learn
Predicts future pH, Turbidity, and TDS values using time-series features
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import json

class WaterQualityPredictor:
    """
    Multi-output predictor for water quality parameters
    Uses sliding window approach for time-series prediction
    """
    
    def __init__(self, window_size=10, prediction_horizon=5):
        """
        Initialize the predictor
        
        Args:
            window_size: Number of past readings to use for prediction
            prediction_horizon: Number of future steps to predict
        """
        self.window_size = window_size
        self.prediction_horizon = prediction_horizon
        
        # Separate models for each parameter
        self.models = {
            'ph': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            ),
            'turbidity': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            ),
            'tds': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        }
        
        self.scalers = {
            'ph': StandardScaler(),
            'turbidity': StandardScaler(),
            'tds': StandardScaler()
        }
        
        self.is_trained = False
        self.training_history = []
        
    def create_sequences(self, data, param):
        """
        Create sliding window sequences for training
        
        Args:
            data: Array of parameter values
            param: Parameter name ('ph', 'turbidity', 'tds')
            
        Returns:
            X: Feature sequences
            y: Target values
        """
        X, y = [], []
        
        for i in range(len(data) - self.window_size):
            # Features: past window_size values + statistical features
            window = data[i:i + self.window_size]
            
            features = list(window)
            # Add statistical features
            features.extend([
                np.mean(window),
                np.std(window),
                np.min(window),
                np.max(window),
                window[-1] - window[0],  # Trend
                np.percentile(window, 25),
                np.percentile(window, 75)
            ])
            
            X.append(features)
            y.append(data[i + self.window_size])
            
        return np.array(X), np.array(y)
    
    def generate_synthetic_data(self, n_samples=5000):
        """
        Generate realistic synthetic water quality data for training
        """
        np.random.seed(42)
        
        # Time component (seasonal patterns)
        t = np.linspace(0, 100, n_samples)
        
        # pH: Normal range 6.5-8.5, with daily fluctuations
        ph_base = 7.0 + 0.5 * np.sin(2 * np.pi * t / 24)  # Daily cycle
        ph_noise = np.random.normal(0, 0.2, n_samples)
        ph_trend = 0.001 * t  # Slight upward trend
        ph = np.clip(ph_base + ph_noise + ph_trend, 5.5, 9.0)
        
        # Turbidity: 0-100 NTU, higher variability
        turb_base = 15 + 10 * np.sin(2 * np.pi * t / 48)  # 2-day cycle
        turb_noise = np.random.exponential(3, n_samples)  # Right-skewed noise
        turb_spikes = np.random.choice([0, 20, 50], n_samples, p=[0.95, 0.04, 0.01])
        turbidity = np.clip(turb_base + turb_noise + turb_spikes, 0, 100)
        
        # TDS: 100-500 ppm, correlated with turbidity
        tds_base = 250 + 50 * np.sin(2 * np.pi * t / 72)  # 3-day cycle
        tds_noise = np.random.normal(0, 20, n_samples)
        tds_corr = 0.5 * turbidity  # Correlation with turbidity
        tds = np.clip(tds_base + tds_noise + tds_corr, 50, 800)
        
        return {
            'ph': ph,
            'turbidity': turbidity,
            'tds': tds,
            'timestamp': [datetime.now() - timedelta(minutes=5*i) for i in range(n_samples)][::-1]
        }
    
    def train(self, data=None, verbose=True):
        """
        Train all parameter models
        
        Args:
            data: Dict with 'ph', 'turbidity', 'tds' arrays. If None, uses synthetic data.
            verbose: Print training progress
        """
        if data is None:
            if verbose:
                print("Generating synthetic training data...")
            data = self.generate_synthetic_data()
        
        results = {}
        
        for param in ['ph', 'turbidity', 'tds']:
            if verbose:
                print(f"\nTraining {param.upper()} model...")
            
            # Create sequences
            X, y = self.create_sequences(data[param], param)
            
            # Scale features
            X_scaled = self.scalers[param].fit_transform(X)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.models[param].fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.models[param].predict(X_test)
            
            metrics = {
                'mae': mean_absolute_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2': r2_score(y_test, y_pred)
            }
            
            results[param] = metrics
            
            if verbose:
                print(f"  MAE: {metrics['mae']:.4f}")
                print(f"  RMSE: {metrics['rmse']:.4f}")
                print(f"  R²: {metrics['r2']:.4f}")
        
        self.is_trained = True
        self.training_history.append({
            'timestamp': datetime.now().isoformat(),
            'results': results
        })
        
        return results
    
    def predict_next(self, history, param, steps=5):
        """
        Predict next values for a parameter
        
        Args:
            history: List of recent values (at least window_size)
            param: Parameter name
            steps: Number of steps to predict
            
        Returns:
            List of predicted values
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        if len(history) < self.window_size:
            raise ValueError(f"Need at least {self.window_size} historical values")
        
        predictions = []
        current_history = list(history[-self.window_size:])
        
        for _ in range(steps):
            # Create features
            window = np.array(current_history[-self.window_size:])
            features = list(window)
            features.extend([
                np.mean(window),
                np.std(window),
                np.min(window),
                np.max(window),
                window[-1] - window[0],
                np.percentile(window, 25),
                np.percentile(window, 75)
            ])
            
            # Scale and predict
            X = self.scalers[param].transform([features])
            pred = self.models[param].predict(X)[0]
            
            predictions.append(pred)
            current_history.append(pred)
        
        return predictions
    
    def predict_all(self, ph_history, turbidity_history, tds_history, steps=5):
        """
        Predict future values for all parameters
        
        Args:
            ph_history: List of recent pH values
            turbidity_history: List of recent turbidity values
            tds_history: List of recent TDS values
            steps: Number of future steps to predict
            
        Returns:
            Dict with predictions for each parameter
        """
        return {
            'ph': self.predict_next(ph_history, 'ph', steps),
            'turbidity': self.predict_next(turbidity_history, 'turbidity', steps),
            'tds': self.predict_next(tds_history, 'tds', steps),
            'prediction_intervals': [f"+{(i+1)*5} min" for i in range(steps)]
        }
    
    def detect_anomaly(self, ph, turbidity, tds):
        """
        Detect if current values are anomalous
        
        Returns:
            Dict with anomaly status and reasons
        """
        anomalies = []
        severity = 'normal'
        
        # pH thresholds (WHO guidelines: 6.5-8.5)
        if ph < 6.0 or ph > 9.0:
            anomalies.append(f"pH critically out of range: {ph:.2f}")
            severity = 'critical'
        elif ph < 6.5 or ph > 8.5:
            anomalies.append(f"pH out of safe range: {ph:.2f}")
            if severity != 'critical':
                severity = 'warning'
        
        # Turbidity thresholds (WHO: <5 NTU ideal, <1 for drinking)
        if turbidity > 50:
            anomalies.append(f"Turbidity critically high: {turbidity:.1f} NTU")
            severity = 'critical'
        elif turbidity > 10:
            anomalies.append(f"Turbidity elevated: {turbidity:.1f} NTU")
            if severity != 'critical':
                severity = 'warning'
        
        # TDS thresholds (WHO: <500 ppm acceptable, >1000 unpalatable)
        if tds > 1000:
            anomalies.append(f"TDS critically high: {tds:.0f} ppm")
            severity = 'critical'
        elif tds > 500:
            anomalies.append(f"TDS elevated: {tds:.0f} ppm")
            if severity != 'critical':
                severity = 'warning'
        
        return {
            'is_anomaly': len(anomalies) > 0,
            'severity': severity,
            'anomalies': anomalies,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_model(self, path='water_quality_model.joblib'):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        save_dict = {
            'models': self.models,
            'scalers': self.scalers,
            'window_size': self.window_size,
            'prediction_horizon': self.prediction_horizon,
            'training_history': self.training_history
        }
        
        joblib.dump(save_dict, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path='water_quality_model.joblib'):
        """Load trained model from disk"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        save_dict = joblib.load(path)
        
        self.models = save_dict['models']
        self.scalers = save_dict['scalers']
        self.window_size = save_dict['window_size']
        self.prediction_horizon = save_dict['prediction_horizon']
        self.training_history = save_dict['training_history']
        self.is_trained = True
        
        print(f"Model loaded from {path}")


# Training script
if __name__ == "__main__":
    print("=" * 60)
    print("Water Quality Prediction Model - Training")
    print("=" * 60)
    
    # Initialize predictor
    predictor = WaterQualityPredictor(window_size=10, prediction_horizon=5)
    
    # Train on synthetic data
    results = predictor.train(verbose=True)
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'water_quality_model.joblib')
    predictor.save_model(model_path)
    
    # Test prediction
    print("\n" + "=" * 60)
    print("Testing Predictions")
    print("=" * 60)
    
    # Generate test data
    test_data = predictor.generate_synthetic_data(100)
    
    # Get predictions
    predictions = predictor.predict_all(
        ph_history=list(test_data['ph'][:20]),
        turbidity_history=list(test_data['turbidity'][:20]),
        tds_history=list(test_data['tds'][:20]),
        steps=5
    )
    
    print("\nPredicted values for next 25 minutes (5-min intervals):")
    print(f"  pH: {[f'{p:.2f}' for p in predictions['ph']]}")
    print(f"  Turbidity: {[f'{p:.1f}' for p in predictions['turbidity']]}")
    print(f"  TDS: {[f'{p:.0f}' for p in predictions['tds']]}")
    
    # Test anomaly detection
    print("\n" + "=" * 60)
    print("Testing Anomaly Detection")
    print("=" * 60)
    
    # Normal values
    result = predictor.detect_anomaly(ph=7.2, turbidity=5, tds=300)
    print(f"\nNormal water (pH=7.2, turbidity=5, TDS=300):")
    print(f"  Anomaly: {result['is_anomaly']}, Severity: {result['severity']}")
    
    # Warning values
    result = predictor.detect_anomaly(ph=8.8, turbidity=15, tds=600)
    print(f"\nWarning water (pH=8.8, turbidity=15, TDS=600):")
    print(f"  Anomaly: {result['is_anomaly']}, Severity: {result['severity']}")
    print(f"  Issues: {result['anomalies']}")
    
    # Critical values
    result = predictor.detect_anomaly(ph=5.5, turbidity=60, tds=1200)
    print(f"\nCritical water (pH=5.5, turbidity=60, TDS=1200):")
    print(f"  Anomaly: {result['is_anomaly']}, Severity: {result['severity']}")
    print(f"  Issues: {result['anomalies']}")
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
