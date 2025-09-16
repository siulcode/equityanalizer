import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


# Load and parse the CSV file
def load_data(file_path):
    df = pd.read_csv(file_path, sep=';', header=None)
    df.columns = ['Timestamp', 'Equity', 'Balance', 'Drawdown']
    df['Timestamp'] = pd.to_datetime(df['Timestamp'],
                                     format='%Y.%m.%d %H:%M:%S')
    return df


# Combined plot showing both bar chart and time series
def plot_combined_equity_analysis(df):
    # Calculate extremes for bar chart
    min_equity = df['Equity'].min()
    max_equity = df['Equity'].max()
    min_equity_date = df.loc[df['Equity'].idxmin(), 'Timestamp']
    max_equity_date = df.loc[df['Equity'].idxmax(), 'Timestamp']
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 10))
    
    # Left side: Bar chart (1/3 of the width)
    ax1 = plt.subplot(1, 3, 1)
    
    # Create bar graph
    categories = ['Lowest\nEquity', 'Highest\nEquity']
    values = [min_equity, max_equity]
    colors = ['red', 'green']
    
    bars = ax1.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on top of bars
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_equity*0.01,
                f'${value:,.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Add date information below bars
    ax1.text(0, min_equity - max_equity*0.08, 
             f'{min_equity_date.strftime("%Y-%m-%d\n%H:%M:%S")}', 
             ha='center', va='top', fontsize=9, style='italic')
    ax1.text(1, max_equity - max_equity*0.08, 
             f'{max_equity_date.strftime("%Y-%m-%d\n%H:%M:%S")}', 
             ha='center', va='top', fontsize=9, style='italic')
    
    ax1.set_title('Equity Extremes', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Equity Value ($)', fontsize=11)
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.set_ylim(min_equity - max_equity*0.15, max_equity + max_equity*0.1)
    
    # Right side: Time series plots (2/3 of the width)
    # Equity and Balance
    ax2 = plt.subplot(2, 3, 2)
    ax2_span = plt.subplot(2, 3, (2, 3))  # Span columns 2 and 3
    
    ax2_span.plot(df['Timestamp'], df['Equity'], label='Equity', color='blue', linewidth=1.5)
    ax2_span.plot(df['Timestamp'], df['Balance'], label='Balance', color='green', linestyle='--', linewidth=1.5)
    ax2_span.set_title('Equity vs Balance Over Time', fontsize=14, fontweight='bold')
    ax2_span.set_xlabel('Time', fontsize=11)
    ax2_span.set_ylabel('Value ($)', fontsize=11)
    ax2_span.legend(fontsize=10)
    ax2_span.grid(True, alpha=0.3)
    
    # Drawdown (bottom right)
    ax3 = plt.subplot(2, 3, (5, 6))  # Span columns 2 and 3 on bottom row
    ax3.plot(df['Timestamp'], df['Drawdown'], label='Drawdown', color='red', linewidth=1.5)
    ax3.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Time', fontsize=11)
    ax3.set_ylabel('Drawdown ($)', fontsize=11)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()




# Example usage
if __name__ == "__main__":
    file_path = 'EquityLogClean.csv'  # Replace with your actual file path
    df = load_data(file_path)
    
    # Display combined equity analysis
    plot_combined_equity_analysis(df)
