"""
Train anomaly detection model for water quality monitoring
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os


def load_data(filepath: str = 'data/water_quality_data.csv') -> pd.DataFrame:
    """Load training data"""
    if not os.path.exists(filepath):
        print(f"Data file not found. Generating data...")
        from generate_data import main as generate_main
        generate_main()
    
    return pd.read_csv(filepath)


def prepare_features(df: pd.DataFrame) -> tuple:
    """Prepare features for training"""
    feature_cols = ['ph', 'tds', 'turbidity', 'flow_rate', 'water_level']
    
    X = df[feature_cols].values
    y = df['is_anomaly'].values
    
    return X, y, feature_cols


def train_model(X: np.ndarray, contamination: float = 0.1) -> tuple:
    """Train Isolation Forest model"""
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        max_samples='auto',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_scaled)
    
    return model, scaler


def evaluate_model(model, scaler, X: np.ndarray, y: np.ndarray):
    """Evaluate model performance"""
    X_scaled = scaler.transform(X)
    
    # Get predictions (-1 for anomaly, 1 for normal)
    y_pred = model.predict(X_scaled)
    
    # Convert to binary (0 for normal, 1 for anomaly)
    y_pred_binary = (y_pred == -1).astype(int)
    
    print("\nModel Evaluation:")
    print("=" * 50)
    print("\nClassification Report:")
    print(classification_report(y, y_pred_binary, target_names=['Normal', 'Anomaly']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y, y_pred_binary)
    print(f"  True Negatives:  {cm[0][0]}")
    print(f"  False Positives: {cm[0][1]}")
    print(f"  False Negatives: {cm[1][0]}")
    print(f"  True Positives:  {cm[1][1]}")
    
    # Calculate metrics
    accuracy = (cm[0][0] + cm[1][1]) / cm.sum()
    precision = cm[1][1] / (cm[1][1] + cm[0][1]) if (cm[1][1] + cm[0][1]) > 0 else 0
    recall = cm[1][1] / (cm[1][1] + cm[1][0]) if (cm[1][1] + cm[1][0]) > 0 else 0
    
    print(f"\nMetrics:")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    
    return y_pred_binary


def save_model(model, scaler, output_dir: str = '../backend/models'):
    """Save trained model and scaler"""
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, 'anomaly_detector.joblib')
    scaler_path = os.path.join(output_dir, 'anomaly_detector_scaler.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"\nModel saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")


def main():
    print("=" * 50)
    print("Water Quality Anomaly Detection - Model Training")
    print("=" * 50)
    
    # Load data
    print("\n1. Loading data...")
    df = load_data()
    print(f"   Loaded {len(df)} samples")
    
    # Prepare features
    print("\n2. Preparing features...")
    X, y, feature_cols = prepare_features(df)
    print(f"   Features: {feature_cols}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples: {len(X_test)}")
    
    # Calculate contamination ratio from training data
    contamination = y_train.mean()
    print(f"   Contamination ratio: {contamination:.4f}")
    
    # Train model
    print("\n3. Training Isolation Forest...")
    model, scaler = train_model(X_train, contamination)
    print("   Model trained successfully!")
    
    # Evaluate on test set
    print("\n4. Evaluating model on test set...")
    evaluate_model(model, scaler, X_test, y_test)
    
    # Save model
    print("\n5. Saving model...")
    save_model(model, scaler)
    
    print("\n" + "=" * 50)
    print("Training complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
