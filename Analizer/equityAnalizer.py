import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
import pytz
from matplotlib.ticker import FuncFormatter, MaxNLocator, FixedLocator, FixedFormatter, NullLocator, NullFormatter


# Load and parse the CSV file
def load_data(file_path):
    df = pd.read_csv(file_path, sep=';', header=None)
    df.columns = ['Timestamp', 'Equity', 'Balance', 'Drawdown']
    
    # Parse timestamps - they are in UTC and need to be converted to Eastern time (EST/EDT)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'],
                                     format='%Y.%m.%d %H:%M:%S')
    
    # Localize to UTC first, then convert to US/Eastern timezone
    utc = pytz.timezone('UTC')
    eastern = pytz.timezone('US/Eastern')
    
    # Localize to UTC first, then convert to Eastern time
    df['Timestamp'] = df['Timestamp'].dt.tz_localize(utc).dt.tz_convert(eastern)
    
    return df


# Combined plot showing both bar chart and time series
def plot_combined_equity_analysis(df, save_path=None):
    # Calculate extremes for bar chart
    min_equity = df['Equity'].min()
    max_equity = df['Equity'].max()
    max_balance = df['Balance'].max()
    min_equity_date = df.loc[df['Equity'].idxmin(), 'Timestamp']
    max_balance_date = df.loc[df['Balance'].idxmax(), 'Timestamp']
    
    # Calculate Gain (final balance - initial balance)
    initial_balance = df['Balance'].iloc[0]
    final_balance = df['Balance'].iloc[-1]
    gain = final_balance - initial_balance
    
    # Calculate Max Floating (negative) Balance - maximum unrealized loss during open positions
    # This represents the largest difference between Balance and Equity (when Balance > Equity)
    df['Floating_Loss'] = df['Balance'] - df['Equity']
    max_floating_loss = df['Floating_Loss'].max()
    max_floating_balance = max_floating_loss * -1  # Make it negative to represent a loss
    max_floating_date = df.loc[df['Floating_Loss'].idxmax(), 'Timestamp']
    
    # Calculate time interval for title
    first_timestamp = df['Timestamp'].min()
    last_timestamp = df['Timestamp'].max()
    duration = last_timestamp - first_timestamp
    
    # Create figure with subplots (make it slightly wider to accommodate wider left panel)
    fig = plt.figure(figsize=(21, 10))
    
    # Add main title with data interval (showing EST/EDT timezone)
    first_tz = first_timestamp.strftime('%Z')  # Get timezone abbreviation (EST or EDT)
    interval_title = f"Data Interval: {first_timestamp.strftime('%Y.%m.%d %H:%M:%S')} to {last_timestamp.strftime('%Y.%m.%d %H:%M:%S')} {first_tz} (Duration: {duration})"
    fig.suptitle(interval_title, fontsize=16, fontweight='bold', y=0.98)
    
    # Left side: Bar chart (slightly smaller width - using 7-column layout)
    ax1 = plt.subplot(1, 7, (1, 2))  # Span columns 1 and 2 to make it moderately wide
    
    # Create bar graph with 4 bars
    categories = ['Lowest\nEquity', 'Highest\nBalance', 'Gain', 'Max Floating\nBalance']
    # For display purposes, show Max Floating Balance as positive (upward bar) but keep the actual negative value for labeling
    display_values = [min_equity, max_balance, gain, abs(max_floating_balance)]  # Make floating balance positive for bar height
    actual_values = [min_equity, max_balance, gain, max_floating_balance]  # Keep actual values for labels
    colors = ['red', 'green', '#228B22', 'orange']  # Using dollar green (#228B22) for Gain bar
    
    bars = ax1.bar(categories, display_values, color=colors, alpha=0.7, edgecolor='black', width=0.6)
    
    # Add value labels on top of bars
    max_display_value = max(display_values)
    
    for i, (bar, actual_value, display_value) in enumerate(zip(bars, actual_values, display_values)):
        # Always put labels on top of bars since all bars now go upward
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_display_value*0.01,
                f'${actual_value:,.2f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Add date information below relevant bars
    min_date_str = min_equity_date.strftime("%Y-%m-%d\n%H:%M:%S")
    max_balance_date_str = max_balance_date.strftime("%Y-%m-%d\n%H:%M:%S")
    max_floating_date_str = max_floating_date.strftime("%Y-%m-%d\n%H:%M:%S")
    
    min_display_value = min(display_values)
    y_position = min_display_value - abs(max_display_value)*0.12
    
    # Show dates below Lowest Equity, Highest Balance, and Max Floating Balance bars
    ax1.text(0, y_position, 
             min_date_str, 
             ha='center', va='top', fontsize=8, style='italic')
    ax1.text(1, y_position, 
             max_balance_date_str, 
             ha='center', va='top', fontsize=8, style='italic')
    ax1.text(3, y_position,  # Position 3 is the Max Floating Balance bar
             max_floating_date_str, 
             ha='center', va='top', fontsize=8, style='italic')
    
    ax1.set_title('Trading Performance Metrics', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Value ($)', fontsize=10)
    ax1.grid(True, axis='y', alpha=0.3)
    
    # Set y-limits using display values (all positive bars)
    y_range = max_display_value - min_display_value
    ax1.set_ylim(min_display_value - y_range*0.2, max_display_value + y_range*0.15)
    
    # Rotate x-axis labels for better readability
    ax1.tick_params(axis='x', rotation=15, labelsize=9)
    
    # Right side: Time series plots (5/7 of the width)
    # Equity and Balance
    ax2_span = plt.subplot(2, 7, (3, 7))  # Span columns 3, 4, 5, 6, and 7
    
    ax2_span.plot(df['Timestamp'], df['Equity'], label='Equity', color='blue', linewidth=1.5)
    ax2_span.plot(df['Timestamp'], df['Balance'], label='Balance', color='green', linestyle='--', linewidth=1.5)
    ax2_span.set_title('Equity vs Balance Over Time', fontsize=14, fontweight='bold')
    ax2_span.set_xlabel('Date and Time', fontsize=12)
    ax2_span.set_ylabel('Value ($)', fontsize=11)
    ax2_span.legend(fontsize=10)
    ax2_span.grid(True, alpha=0.3)
    
    # Simple approach with FixedLocator and FixedFormatter
    y_min = df['Equity'].min()
    y_max = df['Balance'].max()
    
    # Create exactly 5 tick positions
    tick_positions = np.linspace(y_min, y_max, 5)
    tick_labels = [f'${pos:,.0f}' for pos in tick_positions]
    
    # Use FixedLocator and FixedFormatter for complete control
    ax2_span.yaxis.set_major_locator(FixedLocator(tick_positions))
    ax2_span.yaxis.set_major_formatter(FixedFormatter(tick_labels))
    ax2_span.yaxis.set_minor_locator(FixedLocator([]))  # No minor ticks
    
    # Use FixedLocator and FixedFormatter for the axis structure
    ax2_span.yaxis.set_major_locator(FixedLocator(tick_positions))
    ax2_span.yaxis.set_major_formatter(FixedFormatter(tick_labels))
    ax2_span.yaxis.set_minor_locator(FixedLocator([]))  # No minor ticks
    
    # Style the ticks
    ax2_span.tick_params(axis='y', labelsize=10)
    
    # Manually place our clean dollar labels for better visibility
    for pos, label in zip(tick_positions, tick_labels):
        ax2_span.text(-0.005, pos, label, transform=ax2_span.get_yaxis_transform(),
                     ha='right', va='center', fontsize=10, color='black',
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
    
    # Format x-axis to show date and time in single line format (Eastern time)
    eastern_tz = pytz.timezone('US/Eastern')
    ax2_span.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M', tz=eastern_tz))
    ax2_span.xaxis.set_major_locator(mdates.MinuteLocator(interval=30, tz=eastern_tz))  # Show every 30 minutes
    
    # Rotate labels for better readability and increase font size
    ax2_span.tick_params(axis='x', rotation=45, labelsize=8)
    
    # Adjust layout to prevent label cutoff
    plt.setp(ax2_span.xaxis.get_majorticklabels(), ha='right')
    
    # Drawdown (bottom right)
    ax3 = plt.subplot(2, 7, (10, 14))  # Span columns 3, 4, 5, 6, and 7 on bottom row
    ax3.plot(df['Timestamp'], df['Drawdown'], label='Drawdown', color='red', linewidth=1.5)
    ax3.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Date and Time', fontsize=12)
    ax3.set_ylabel('Drawdown (%)', fontsize=11)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # Convert drawdown ratio to dollar amounts for better understanding
    # The drawdown data appears to be stored as (Balance - Equity) / Balance
    # Let's calculate and show actual dollar drawdown amounts
    df['Dollar_Drawdown'] = df['Balance'] - df['Equity']
    
    # Calculate range for drawdown ticks
    dd_min = df['Dollar_Drawdown'].min()
    dd_max = df['Dollar_Drawdown'].max()
    
    # Create 5 evenly spaced tick positions for drawdown
    dd_tick_positions = np.linspace(dd_min, dd_max, 5)
    
    # Create custom tick labels as dollar amounts
    dd_tick_labels = []
    for pos in dd_tick_positions:
        if abs(pos) >= 100:
            dd_tick_labels.append(f'${pos:.0f}')
        elif abs(pos) >= 10:
            dd_tick_labels.append(f'${pos:.1f}')
        else:
            dd_tick_labels.append(f'${pos:.2f}')
    
    # Map the original drawdown values to dollar amounts for plotting
    # We need to plot df['Dollar_Drawdown'] instead of df['Drawdown']
    ax3.clear()  # Clear and replot with correct data
    ax3.plot(df['Timestamp'], df['Dollar_Drawdown'], label='Drawdown', color='red', linewidth=1.5)
    ax3.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Date and Time', fontsize=12)
    ax3.set_ylabel('Drawdown ($)', fontsize=11)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # Use FixedLocator and FixedFormatter for drawdown y-axis
    ax3.yaxis.set_major_locator(FixedLocator(dd_tick_positions))
    ax3.yaxis.set_major_formatter(FixedFormatter(dd_tick_labels))
    ax3.yaxis.set_minor_locator(FixedLocator([]))  # No minor ticks
    
    # Format x-axis to show date and time in single line format (Eastern time)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M', tz=eastern_tz))
    ax3.xaxis.set_major_locator(mdates.MinuteLocator(interval=30, tz=eastern_tz))  # Show every 30 minutes
    
    # Rotate labels for better readability and increase font size
    ax3.tick_params(axis='x', rotation=45, labelsize=8)
    
    # Adjust layout to prevent label cutoff
    plt.setp(ax3.xaxis.get_majorticklabels(), ha='right')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to leave space for main title
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved to: {save_path}")
    else:
        plt.show()




# Example usage
if __name__ == "__main__":
    file_path = 'EquityLogClean.csv'  # Replace with your actual file path
    df = load_data(file_path)
    
    # Display data statistics for debugging
    print(f"Data loaded: {len(df)} rows")
    print(f"Equity range: ${df['Equity'].min():.2f} - ${df['Equity'].max():.2f}")
    print(f"Balance range: ${df['Balance'].min():.2f} - ${df['Balance'].max():.2f}")
    
    # Check for any extreme outliers
    equity_mean = df['Equity'].mean()
    equity_std = df['Equity'].std()
    outliers = df[(df['Equity'] > equity_mean + 3*equity_std) | (df['Equity'] < equity_mean - 3*equity_std)]
    if len(outliers) > 0:
        print(f"Warning: Found {len(outliers)} potential outliers in equity data:")
        print(outliers[['Timestamp', 'Equity', 'Balance']].head())
    
    # Display time interval information
    first_timestamp = df['Timestamp'].min()
    last_timestamp = df['Timestamp'].max()
    duration = last_timestamp - first_timestamp
    timezone_abbr = first_timestamp.strftime('%Z')  # Get timezone abbreviation (EST or EDT)
    
    print(f"Data Interval: {first_timestamp.strftime('%Y.%m.%d %H:%M:%S')} to {last_timestamp.strftime('%Y.%m.%d %H:%M:%S')} {timezone_abbr} (Duration: {duration})")
    print(f"Drawdown range: ${df['Drawdown'].min():.2f} - ${df['Drawdown'].max():.2f}")
    
    # Display combined equity analysis
    plot_combined_equity_analysis(df)
