import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

# Create output directory if it doesn't exist
os.makedirs('flow_density_plots', exist_ok=True)

# Set Seaborn style for better aesthetics
sns.set(style="whitegrid", palette="pastel", font_scale=1.1)
plt.rcParams['figure.figsize'] = (12, 8)

# Create a custom colormap
colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"]
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

df = pd.read_csv('Updated_Assignment.csv')

# Convert columns to numeric
df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
df['Speed Inverse'] = pd.to_numeric(df['Speed Inverse'], errors='coerce')

# Initialize variables
time_intervals = range(0, 235959 + 500, 500)
results = []
plot_count = 0

prev = 0

for current in time_intervals[1:]:
    # Filter rows between previous and current time
    filtered_df = df[(df['Time'] > prev) & (df['Time'] <= current)].copy()
    
    # Only proceed if there are rows in this time interval
    if not filtered_df.empty:
        # Calculate SMS (normalized speed inverse)
        speed_inverse_sum = filtered_df['Speed Inverse'].sum()
        vehicle_count = filtered_df['Time'].count()
        if speed_inverse_sum != 0:  # Avoid division by zero
            filtered_df['SMS'] = vehicle_count/speed_inverse_sum
            filtered_df['Density'] = filtered_df['Q (veh/h)']/filtered_df['SMS']
        else:
            filtered_df['SMS'] = 0
            filtered_df['Density'] = 0
        
        results.append(filtered_df)
        
        # Create plot for this interval if we have valid data
        if (not filtered_df['Density'].isnull().all() and 
            not filtered_df['Q (veh/h)'].isnull().all() and
            len(filtered_df) > 1):  # Need at least 2 points for regression
            
            plot_count += 1
            
            plt.figure(figsize=(14, 8))
            
            try:
                # Create scatter plot (without regression line first)
                scatter = plt.scatter(
                    x=filtered_df['Density'],
                    y=filtered_df['Q (veh/h)'],
                    s=100,
                    alpha=0.7,
                    edgecolor='w',
                    linewidth=1
                )
                
                # Add regression line separately
                sns.regplot(
                    x='Density', 
                    y='Q (veh/h)', 
                    data=filtered_df,
                    scatter=False,
                    line_kws={
                        'color': '#FF6B6B', 
                        'lw': 2
                    },
                    ci=95,
                    truncate=False
                )
                
                # Add title and labels
                time_str = f"{prev:06d}-{current:06d}"
                plt.title(f"Flow-Density Relationship\nTime Interval: {time_str}", 
                         pad=20, fontsize=16, fontweight='bold')
                plt.xlabel('Density (veh/km)', labelpad=15, fontsize=14)
                plt.ylabel('Flow (veh/h)', labelpad=15, fontsize=14)
                
                # Add grid and adjust layout
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                
                # Add a fancy box around the plot
                ax = plt.gca()
                for spine in ax.spines.values():
                    spine.set_edgecolor('#888888')
                    spine.set_linewidth(1.5)
                
                # Save the plot
                filename = f"flow_density_plots/flow_density_plot_{plot_count:02d}_{time_str}.png"
                plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                
                # print(f"Saved plot: {filename}")
                
            except Exception as e:
                print(f"Error creating plot for interval {prev:06d}-{current:06d}: {str(e)}")
                plt.close()
        
        # Create an empty row with same columns
        empty_row = pd.DataFrame({col: np.nan for col in filtered_df.columns}, index=[0])
        results.append(empty_row)
    
    prev = current

# Combine results if any were found
if results:
    final_df = pd.concat(results, ignore_index=True)
    final_df.to_csv('output_with_empty_rows.csv', index=False)
    print("\nSuccess! File saved as 'output_with_empty_rows.csv'")
    # NEW CODE: Create a plot using only Q and Density columns with unique pairs
    try:
        # Select only the two columns we need
        plot_df = final_df[['Q (veh/h)', 'Density']].copy()
        
        # Remove rows where either column is NaN
        plot_df = plot_df.dropna()
        
        # Remove duplicate (Q, Density) pairs
        plot_df = plot_df.drop_duplicates()
        
        # Only proceed if we have at least 2 unique points
        if len(plot_df) >= 2:
            plt.figure(figsize=(14, 8))
            
            # Create scatter plot
            plt.scatter(
                x=plot_df['Density'],
                y=plot_df['Q (veh/h)'],
                s=100,
                alpha=0.7,
                edgecolor='w',
                linewidth=1
            )
            
            # Add regression line
            sns.regplot(
                x='Density', 
                y='Q (veh/h)', 
                data=plot_df,
                scatter=False,
                line_kws={
                    'color': '#FF6B6B', 
                    'lw': 2
                },
                ci=95,
                truncate=False
            )
            
            # Add title and labels
            plt.title("Flow-Density Relationship (All Data, Unique Pairs)", 
                     pad=20, fontsize=16, fontweight='bold')
            plt.xlabel('Density (veh/km)', labelpad=15, fontsize=14)
            plt.ylabel('Flow (veh/h)', labelpad=15, fontsize=14)
            
            # Add grid and adjust layout
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # Add a fancy box around the plot
            ax = plt.gca()
            for spine in ax.spines.values():
                spine.set_edgecolor('#888888')
                spine.set_linewidth(1.5)
            
            # Save the plot
            filename = "flow_density_plots/combined_flow_density_unique_pairs.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"Success! Saved combined plot with unique pairs: {filename}")
        else:
            print("Not enough unique data points (need at least 2) for combined plot")
            
    except Exception as e:
        print(f"Error creating combined plot: {str(e)}")
        plt.close()
else:
    print("No data found in any time intervals")