"""
Generate synthetic water quality data for ML model training
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os


def generate_normal_data(n_samples: int = 5000) -> pd.DataFrame:
    """Generate normal (good quality) water data"""
    np.random.seed(42)
    
    data = {
        'ph': np.random.normal(7.0, 0.3, n_samples),
        'tds': np.random.normal(250, 50, n_samples),
        'turbidity': np.random.normal(2.0, 0.5, n_samples),
        'flow_rate': np.random.normal(5.0, 1.5, n_samples),
        'water_level': np.random.normal(60, 15, n_samples),
        'temperature': np.random.normal(26, 2, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Clip to realistic ranges
    df['ph'] = df['ph'].clip(6.5, 8.5)
    df['tds'] = df['tds'].clip(100, 400)
    df['turbidity'] = df['turbidity'].clip(0.5, 4.0)
    df['flow_rate'] = df['flow_rate'].clip(1.0, 10.0)
    df['water_level'] = df['water_level'].clip(20, 95)
    df['temperature'] = df['temperature'].clip(20, 35)
    
    df['is_anomaly'] = 0
    df['anomaly_type'] = 'none'
    
    return df


def generate_anomaly_data(n_samples: int = 500) -> pd.DataFrame:
    """Generate anomalous water data"""
    np.random.seed(123)
    
    anomaly_types = [
        'high_ph', 'low_ph', 'high_tds', 'high_turbidity',
        'low_flow', 'low_level', 'contamination'
    ]
    
    samples_per_type = n_samples // len(anomaly_types)
    dfs = []
    
    for atype in anomaly_types:
        # Start with normal data
        data = {
            'ph': np.random.normal(7.0, 0.3, samples_per_type),
            'tds': np.random.normal(250, 50, samples_per_type),
            'turbidity': np.random.normal(2.0, 0.5, samples_per_type),
            'flow_rate': np.random.normal(5.0, 1.5, samples_per_type),
            'water_level': np.random.normal(60, 15, samples_per_type),
            'temperature': np.random.normal(26, 2, samples_per_type),
        }
        
        df = pd.DataFrame(data)
        
        # Apply anomaly
        if atype == 'high_ph':
            df['ph'] = np.random.uniform(8.5, 10.0, samples_per_type)
        elif atype == 'low_ph':
            df['ph'] = np.random.uniform(4.0, 6.0, samples_per_type)
        elif atype == 'high_tds':
            df['tds'] = np.random.uniform(500, 1000, samples_per_type)
        elif atype == 'high_turbidity':
            df['turbidity'] = np.random.uniform(5.0, 15.0, samples_per_type)
        elif atype == 'low_flow':
            df['flow_rate'] = np.random.uniform(0.0, 0.5, samples_per_type)
        elif atype == 'low_level':
            df['water_level'] = np.random.uniform(0, 10, samples_per_type)
        elif atype == 'contamination':
            # Multiple metrics affected
            df['ph'] = np.random.uniform(5.0, 9.5, samples_per_type)
            df['tds'] = np.random.uniform(400, 800, samples_per_type)
            df['turbidity'] = np.random.uniform(4.0, 10.0, samples_per_type)
        
        df['is_anomaly'] = 1
        df['anomaly_type'] = atype
        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)


def add_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Add realistic timestamps to the data"""
    n = len(df)
    base_time = datetime.now() - timedelta(days=30)
    
    timestamps = []
    for i in range(n):
        # Random time within 30 days
        offset = timedelta(
            days=np.random.randint(0, 30),
            hours=np.random.randint(0, 24),
            minutes=np.random.randint(0, 60)
        )
        timestamps.append(base_time + offset)
    
    df['timestamp'] = timestamps
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df


def calculate_quality_score(row: pd.Series) -> float:
    """Calculate water quality score (0-100)"""
    score = 100.0
    
    # pH scoring (ideal: 6.5-8.5)
    if row['ph'] < 6.5:
        score -= (6.5 - row['ph']) * 15
    elif row['ph'] > 8.5:
        score -= (row['ph'] - 8.5) * 15
    
    # TDS scoring (ideal: < 500)
    if row['tds'] > 300:
        score -= (row['tds'] - 300) / 10
    
    # Turbidity scoring (ideal: < 5)
    if row['turbidity'] > 2:
        score -= (row['turbidity'] - 2) * 5
    
    # Flow rate scoring
    if row['flow_rate'] < 1:
        score -= 10
    
    # Water level scoring
    if row['water_level'] < 20:
        score -= (20 - row['water_level'])
    
    return max(0, min(100, score))


def main():
    print("Generating training data...")
    
    # Generate data
    normal_df = generate_normal_data(5000)
    anomaly_df = generate_anomaly_data(500)
    
    # Combine
    df = pd.concat([normal_df, anomaly_df], ignore_index=True)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Add timestamps
    df = add_timestamps(df)
    
    # Calculate quality scores
    df['quality_score'] = df.apply(calculate_quality_score, axis=1)
    
    # Create output directory
    os.makedirs('data', exist_ok=True)
    
    # Save data
    df.to_csv('data/water_quality_data.csv', index=False)
    
    # Save summary
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {len(df)}")
    print(f"  Normal samples: {(df['is_anomaly'] == 0).sum()}")
    print(f"  Anomaly samples: {(df['is_anomaly'] == 1).sum()}")
    print(f"\nFeature ranges:")
    for col in ['ph', 'tds', 'turbidity', 'flow_rate', 'water_level', 'quality_score']:
        print(f"  {col}: {df[col].min():.2f} - {df[col].max():.2f} (mean: {df[col].mean():.2f})")
    
    print(f"\nData saved to data/water_quality_data.csv")
    
    return df


if __name__ == "__main__":
    main()
