import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
import pytz


# Load and parse the CSV file
def load_data(file_path):
    df = pd.read_csv(file_path, sep=';', header=None)
    df.columns = ['Timestamp', 'Equity', 'Balance', 'Drawdown']
    
    # Parse timestamps and assume they are already in Eastern time (EST/EDT)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'],
                                     format='%Y.%m.%d %H:%M:%S')
    
    # Assume the original timestamps are already in US/Eastern timezone
    eastern = pytz.timezone('US/Eastern')
    
    # Localize to Eastern time (no conversion needed)
    df['Timestamp'] = df['Timestamp'].dt.tz_localize(eastern)
    
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
    
    # Left side: Bar chart (narrower - 1/4 of the width)
    ax1 = plt.subplot(1, 4, 1)
    
    # Create bar graph with thinner bars
    categories = ['Lowest\nEquity', 'Highest\nEquity']
    values = [min_equity, max_equity]
    colors = ['red', 'green']
    
    bars = ax1.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', width=0.6)
    
    # Add value labels on top of bars
    for i, (bar, value) in enumerate(zip(bars, values)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_equity*0.01,
                f'${value:,.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Add date information below bars
    min_date_str = min_equity_date.strftime("%Y-%m-%d\n%H:%M:%S")
    max_date_str = max_equity_date.strftime("%Y-%m-%d\n%H:%M:%S")
    
    ax1.text(0, min_equity - max_equity*0.08, 
             min_date_str, 
             ha='center', va='top', fontsize=9, style='italic')
    ax1.text(1, max_equity - max_equity*0.08, 
             max_date_str, 
             ha='center', va='top', fontsize=9, style='italic')
    
    ax1.set_title('Equity Extremes', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Equity Value ($)', fontsize=11)
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.set_ylim(min_equity - max_equity*0.15, max_equity + max_equity*0.1)
    
    # Right side: Time series plots (3/4 of the width)
    # Equity and Balance
    ax2 = plt.subplot(2, 4, 2)
    ax2_span = plt.subplot(2, 4, (2, 4))  # Span columns 2, 3, and 4
    
    ax2_span.plot(df['Timestamp'], df['Equity'], label='Equity', color='blue', linewidth=1.5)
    ax2_span.plot(df['Timestamp'], df['Balance'], label='Balance', color='green', linestyle='--', linewidth=1.5)
    ax2_span.set_title('Equity vs Balance Over Time', fontsize=14, fontweight='bold')
    ax2_span.set_xlabel('Date and Time', fontsize=12)
    ax2_span.set_ylabel('Value ($)', fontsize=11)
    ax2_span.legend(fontsize=10)
    ax2_span.grid(True, alpha=0.3)
    
    # Format x-axis to show date and time in MM.DD-HH:MM format
    ax2_span.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d-%H:%M'))
    ax2_span.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))  # Show every 15 minutes
    
    # Rotate labels for better readability and increase font size
    ax2_span.tick_params(axis='x', rotation=45, labelsize=10)
    
    # Adjust layout to prevent label cutoff
    plt.setp(ax2_span.xaxis.get_majorticklabels(), ha='right')
    
    # Drawdown (bottom right)
    ax3 = plt.subplot(2, 4, (6, 8))  # Span columns 2, 3, and 4 on bottom row
    ax3.plot(df['Timestamp'], df['Drawdown'], label='Drawdown', color='red', linewidth=1.5)
    ax3.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Date and Time', fontsize=12)
    ax3.set_ylabel('Drawdown ($)', fontsize=11)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # Format x-axis to show date and time in MM.DD-HH:MM format
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d-%H:%M'))
    ax3.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))  # Show every 15 minutes
    
    # Rotate labels for better readability and increase font size
    ax3.tick_params(axis='x', rotation=45, labelsize=10)
    
    # Adjust layout to prevent label cutoff
    plt.setp(ax3.xaxis.get_majorticklabels(), ha='right')
    
    plt.tight_layout()
    plt.show()




# Example usage
if __name__ == "__main__":
    file_path = 'EquityLogClean.csv'  # Replace with your actual file path
    df = load_data(file_path)
    
    # Display combined equity analysis
    plot_combined_equity_analysis(df)
