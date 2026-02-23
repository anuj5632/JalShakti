"""
ML Engine - Anomaly detection and water quality scoring
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, List, Tuple, Optional
from config import settings, WATER_QUALITY_STANDARDS


class MLEngine:
    def __init__(self):
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names = ['ph', 'tds', 'turbidity', 'flow_rate', 'water_level']
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if available"""
        model_path = settings.MODEL_PATH
        scaler_path = model_path.replace('.joblib', '_scaler.joblib')
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                print("✓ ML model loaded successfully")
            except Exception as e:
                print(f"⚠ Error loading model: {e}")
                self._create_default_model()
        else:
            print("⚠ No pre-trained model found. Using default model.")
            self._create_default_model()
    
    def _create_default_model(self):
        """Create and fit a default model with synthetic data"""
        # Generate synthetic normal water quality data
        np.random.seed(42)
        n_samples = 1000
        
        normal_data = np.column_stack([
            np.random.normal(7.0, 0.3, n_samples),      # pH (6.5-7.5)
            np.random.normal(250, 50, n_samples),       # TDS (150-350)
            np.random.normal(2.0, 0.5, n_samples),      # Turbidity (1-3)
            np.random.normal(5.0, 1.5, n_samples),      # Flow rate (2-8)
            np.random.normal(60, 15, n_samples)         # Water level (30-90)
        ])
        
        # Ensure values are within reasonable bounds
        normal_data[:, 0] = np.clip(normal_data[:, 0], 6.5, 8.5)
        normal_data[:, 1] = np.clip(normal_data[:, 1], 50, 500)
        normal_data[:, 2] = np.clip(normal_data[:, 2], 0, 5)
        normal_data[:, 3] = np.clip(normal_data[:, 3], 0.5, 20)
        normal_data[:, 4] = np.clip(normal_data[:, 4], 10, 100)
        
        self.scaler = StandardScaler()
        scaled_data = self.scaler.fit_transform(normal_data)
        
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.model.fit(scaled_data)
    
    def detect_anomaly(self, reading: Dict) -> Tuple[bool, float, List[str]]:
        """
        Detect if a sensor reading is anomalous
        
        Returns:
            (is_anomaly, anomaly_score, anomalous_metrics)
        """
        # Extract features
        features = np.array([[
            reading.get('ph', 7.0),
            reading.get('tds', 200),
            reading.get('turbidity', 2.0),
            reading.get('flow_rate', 5.0),
            reading.get('water_level', 50)
        ]])
        
        # Scale features
        if self.scaler:
            scaled_features = self.scaler.transform(features)
        else:
            scaled_features = features
        
        # Get anomaly score
        anomaly_score = self.model.decision_function(scaled_features)[0]
        prediction = self.model.predict(scaled_features)[0]
        
        is_anomaly = prediction == -1
        
        # Check which metrics are out of range
        anomalous_metrics = []
        
        if reading.get('ph', 7.0) < settings.PH_MIN or reading.get('ph', 7.0) > settings.PH_MAX:
            anomalous_metrics.append('ph')
        
        if reading.get('tds', 200) > settings.TDS_MAX:
            anomalous_metrics.append('tds')
        
        if reading.get('turbidity', 2.0) > settings.TURBIDITY_MAX:
            anomalous_metrics.append('turbidity')
        
        if reading.get('flow_rate', 5.0) < settings.FLOW_MIN:
            anomalous_metrics.append('flow_rate')
        
        if reading.get('water_level', 50) < settings.WATER_LEVEL_MIN:
            anomalous_metrics.append('water_level')
        
        # Consider it an anomaly if thresholds exceeded even if model says no
        if anomalous_metrics and not is_anomaly:
            is_anomaly = True
        
        return is_anomaly, float(anomaly_score), anomalous_metrics
    
    def calculate_quality_score(self, reading: Dict) -> Tuple[float, str, List[str]]:
        """
        Calculate water quality score (0-100) and category
        
        Returns:
            (score, category, recommendations)
        """
        scores = []
        recommendations = []
        
        # pH score (ideal: 6.5-8.5)
        ph = reading.get('ph', 7.0)
        if 6.5 <= ph <= 8.5:
            ph_score = 100 - abs(ph - 7.0) * 10
        elif ph < 6.5:
            ph_score = max(0, 50 - (6.5 - ph) * 20)
            recommendations.append(f"pH is too low ({ph:.1f}). Consider adding alkaline minerals.")
        else:
            ph_score = max(0, 50 - (ph - 8.5) * 20)
            recommendations.append(f"pH is too high ({ph:.1f}). Check water source for contamination.")
        scores.append(('ph', ph_score, 0.25))
        
        # TDS score (ideal: < 500 mg/L)
        tds = reading.get('tds', 200)
        if tds <= 300:
            tds_score = 100
        elif tds <= 500:
            tds_score = 100 - (tds - 300) * 0.25
        else:
            tds_score = max(0, 50 - (tds - 500) * 0.1)
            recommendations.append(f"TDS is high ({tds:.0f} mg/L). Consider water filtration.")
        scores.append(('tds', tds_score, 0.25))
        
        # Turbidity score (ideal: < 5 NTU)
        turbidity = reading.get('turbidity', 2.0)
        if turbidity <= 1:
            turb_score = 100
        elif turbidity <= 5:
            turb_score = 100 - (turbidity - 1) * 12.5
        else:
            turb_score = max(0, 50 - (turbidity - 5) * 10)
            recommendations.append(f"Water is cloudy ({turbidity:.1f} NTU). Check for sediment.")
        scores.append(('turbidity', turb_score, 0.20))
        
        # Flow rate score (good flow indicates working system)
        flow = reading.get('flow_rate', 5.0)
        if flow >= 2:
            flow_score = min(100, 70 + flow * 3)
        elif flow >= 0.5:
            flow_score = 50 + flow * 20
        else:
            flow_score = flow * 100
            recommendations.append("Water flow is low. Check for blockages.")
        scores.append(('flow', flow_score, 0.15))
        
        # Water level score
        level = reading.get('water_level', 50)
        if level >= 30:
            level_score = min(100, 70 + level * 0.3)
        elif level >= 10:
            level_score = 30 + level * 2
        else:
            level_score = level * 3
            recommendations.append("Water level is critically low. Refill tank.")
        scores.append(('level', level_score, 0.15))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        # Determine category
        if total_score >= 90:
            category = "Excellent"
        elif total_score >= 75:
            category = "Good"
        elif total_score >= 50:
            category = "Fair"
        elif total_score >= 25:
            category = "Poor"
        else:
            category = "Critical"
            recommendations.insert(0, "⚠️ Water quality is critically low. Do not use for consumption!")
        
        return round(total_score, 1), category, recommendations
    
    def analyze_reading(self, reading: Dict) -> Dict:
        """
        Complete analysis of a sensor reading
        """
        is_anomaly, anomaly_score, anomalous_metrics = self.detect_anomaly(reading)
        quality_score, category, recommendations = self.calculate_quality_score(reading)
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': anomaly_score,
            'anomalous_metrics': anomalous_metrics,
            'quality_score': quality_score,
            'quality_category': category,
            'recommendations': recommendations
        }
    
    def save_model(self, path: Optional[str] = None):
        """Save the current model"""
        if path is None:
            path = settings.MODEL_PATH
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        joblib.dump(self.scaler, path.replace('.joblib', '_scaler.joblib'))
        print(f"✓ Model saved to {path}")


# Singleton instance
ml_engine = MLEngine()
