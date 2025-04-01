# aggregate data
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Create output directory if it doesn't exist
os.makedirs('aggregated_results', exist_ok=True)

# Read the input data
df = pd.read_csv('Updated_Assignment.csv')

# Convert columns to numeric (handle errors)
numeric_cols = ['Time', 'Speed Inverse', 'Q (veh/h)', 'Headway', 'Gap']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Function to create strict 5-minute intervals
def create_time_intervals():
    intervals = []
    current = datetime.strptime("000000", "%H%M%S")
    end = datetime.strptime("235959", "%H%M%S")
    delta = timedelta(minutes=5)
    
    while current <= end:
        intervals.append(int(current.strftime("%H%M%S")))
        current += delta
    return intervals

time_intervals = create_time_intervals()
aggregated_data = []

for i in range(len(time_intervals)-1):
    start = time_intervals[i]
    end = time_intervals[i+1]
    
    # Filter rows between current interval
    interval_df = df[(df['Time'] > start) & (df['Time'] <= end)].copy()
    
    # Calculate metrics (even for empty intervals)
    vehicle_count = len(interval_df)
    
    # Initialize metrics as NaN for empty intervals
    metrics = {
        'From': f"{start:06d}",
        'To': f"{end:06d}",
        'Vehicle Count': vehicle_count,
        'Time Avg Speed': np.nan,
        'SMS': np.nan,
        'Avg Headway': np.nan,
        'Avg Gap': np.nan
    }
    
    if not interval_df.empty:
        # Speed calculations
        speed_inverse_sum = interval_df['Speed Inverse'].sum()
        metrics['SMS'] = vehicle_count / speed_inverse_sum if speed_inverse_sum != 0 else 0
        
        # Averages
        if 'Headway' in interval_df:
            metrics['Avg Headway'] = interval_df['Headway'].mean()
        if 'Gap' in interval_df:
            metrics['Avg Gap'] = interval_df['Gap'].mean()
        
        if 'Speed' in interval_df.columns:
            metrics['Time Avg Speed'] = interval_df['Speed'].mean()
        else:
            metrics['Time Avg Speed'] = (1 / interval_df['Speed Inverse']).mean() if speed_inverse_sum != 0 else np.nan
    
    aggregated_data.append(metrics)

# Create DataFrame
summary_df = pd.DataFrame(aggregated_data)

# Save to Excel
output_path = 'aggregated_results/traffic_summary_strict_intervals.xlsx'
summary_df.to_excel(output_path, index=False)

print(f"\nAggregation complete! Results saved to: {output_path}")
print("\nFirst 5 rows of the output:")
print(summary_df.head())