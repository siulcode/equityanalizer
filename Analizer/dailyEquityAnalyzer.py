import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
import pytz
import os
import glob
import re
import argparse
import sys
from matplotlib.ticker import FuncFormatter, MaxNLocator, FixedLocator, FixedFormatter


def load_csv_data(file_path):
    """Load and parse a single CSV file with equity data"""
    try:
        df = pd.read_csv(file_path, sep=';', header=None)
        df.columns = ['Timestamp', 'Equity', 'Balance', 'Drawdown']
        
        # Parse timestamps - they are in UTC and need to be converted to Eastern time (EST/EDT)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y.%m.%d %H:%M:%S')
        
        # Localize to UTC first, then convert to US/Eastern timezone
        utc = pytz.timezone('UTC')
        eastern = pytz.timezone('US/Eastern')
        df['Timestamp'] = df['Timestamp'].dt.tz_localize(utc).dt.tz_convert(eastern)
        
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None


def extract_date_from_filename(filename):
    """Extract date from filename in format EquityLogClean_YYYY-MM-DD.csv"""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d').date()
    return None


def calculate_max_floating_negative_balance(df):
    """Calculate the maximum floating negative balance for a single day's data"""
    # Calculate Floating Loss - difference between Balance and Equity (when Balance > Equity)
    df['Floating_Loss'] = df['Balance'] - df['Equity']
    
    # Maximum floating loss during the day
    max_floating_loss = df['Floating_Loss'].max()
    
    # Convert to negative to represent a loss (max negative balance)
    max_floating_negative_balance = max_floating_loss * -1
    
    # Find the timestamp when this maximum occurred
    max_floating_idx = df['Floating_Loss'].idxmax()
    max_floating_timestamp = df.loc[max_floating_idx, 'Timestamp']
    
    # Additional statistics
    min_equity = df['Equity'].min()
    max_balance = df['Balance'].max()
    initial_balance = df['Balance'].iloc[0]
    final_balance = df['Balance'].iloc[-1]
    daily_gain = final_balance - initial_balance
    
    return {
        'max_floating_negative_balance': max_floating_negative_balance,
        'max_floating_timestamp': max_floating_timestamp,
        'min_equity': min_equity,
        'max_balance': max_balance,
        'daily_gain': daily_gain,
        'initial_balance': initial_balance,
        'final_balance': final_balance,
        'data_points': len(df)
    }


def process_all_csv_files(directory_path):
    """Process all CSV files in the directory and calculate daily statistics"""
    # Find all CSV files in the directory
    csv_pattern = os.path.join(directory_path, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found in {directory_path}")
        return None
    
    print(f"Found {len(csv_files)} CSV files to process...")
    
    daily_results = []
    
    for csv_file in sorted(csv_files):
        filename = os.path.basename(csv_file)
        date = extract_date_from_filename(filename)
        
        if date is None:
            print(f"Could not extract date from filename: {filename}")
            continue
            
        print(f"Processing {filename} (Date: {date})...")
        
        df = load_csv_data(csv_file)
        if df is None or df.empty:
            print(f"Skipping {filename} - no valid data")
            continue
            
        stats = calculate_max_floating_negative_balance(df)
        stats['date'] = date
        stats['filename'] = filename
        
        daily_results.append(stats)
        
        # Note: Following the rule about XAUEUR having higher ask/bid prices than XAUUSD
        print(f"  Max floating negative balance: ${stats['max_floating_negative_balance']:,.2f}")
        print(f"  Data points: {stats['data_points']}")
    
    return daily_results


def plot_daily_max_floating_balances(daily_results, save_path=None):
    """Create a comprehensive visualization of daily maximum floating negative balances"""
    if not daily_results:
        print("No data to plot")
        return
    
    # Sort by date
    daily_results = sorted(daily_results, key=lambda x: x['date'])
    
    dates = [result['date'] for result in daily_results]
    max_floating_balances = [result['max_floating_negative_balance'] for result in daily_results]
    daily_gains = [result['daily_gain'] for result in daily_results]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Main title
    date_range = f"{dates[0]} to {dates[-1]}" if len(dates) > 1 else str(dates[0])
    fig.suptitle(f'Daily Trading Analysis: Maximum Floating Negative Balance\n{date_range}', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Top plot: Maximum Floating Negative Balance by Day
    bars1 = ax1.bar(dates, [abs(bal) for bal in max_floating_balances], 
                    color='red', alpha=0.7, edgecolor='black', width=0.8)
    
    ax1.set_title('Maximum Floating Negative Balance by Day', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Max Floating Loss ($)', fontsize=12)
    ax1.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on top of bars
    for i, (bar, balance) in enumerate(zip(bars1, max_floating_balances)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(abs(bal) for bal in max_floating_balances)*0.01,
                f'${balance:,.2f}', ha='center', va='bottom', fontweight='bold', fontsize=10, rotation=0)
    
    # Format x-axis
    ax1.tick_params(axis='x', rotation=45, labelsize=10)
    
    # Bottom plot: Daily Gains/Losses
    colors = ['green' if gain >= 0 else 'red' for gain in daily_gains]
    bars2 = ax2.bar(dates, daily_gains, color=colors, alpha=0.7, edgecolor='black', width=0.8)
    
    ax2.set_title('Daily Gain/Loss by Day', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Daily Gain/Loss ($)', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.grid(True, axis='y', alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, gain) in enumerate(zip(bars2, daily_gains)):
        label_y = bar.get_height() + (max(daily_gains) - min(daily_gains))*0.01 if gain >= 0 else bar.get_height() - (max(daily_gains) - min(daily_gains))*0.03
        ax2.text(bar.get_x() + bar.get_width()/2, label_y,
                f'${gain:,.2f}', ha='center', va='bottom' if gain >= 0 else 'top', 
                fontweight='bold', fontsize=10, rotation=0)
    
    # Format x-axis
    ax2.tick_params(axis='x', rotation=45, labelsize=10)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved to: {save_path}")
    else:
        plt.show()


def show_available_directories():
    """Show some common directories that might contain CSV files"""
    base_path = r"C:\Users\maste\OneDrive\Documentos\archived_logs"
    
    print("\nLooking for available directories in archived_logs...")
    if os.path.exists(base_path):
        try:
            subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            if subdirs:
                print(f"\nFound directories in {base_path}:")
                for i, subdir in enumerate(subdirs, 1):
                    full_path = os.path.join(base_path, subdir)
                    csv_count = len(glob.glob(os.path.join(full_path, "*.csv")))
                    print(f"  {i}. {subdir} ({csv_count} CSV files)")
            else:
                print(f"No subdirectories found in {base_path}")
        except PermissionError:
            print(f"Permission denied accessing {base_path}")
    else:
        print(f"Directory {base_path} does not exist")


def print_summary_statistics(daily_results):
    """Print summary statistics for all days"""
    if not daily_results:
        return
    
    max_floating_balances = [result['max_floating_negative_balance'] for result in daily_results]
    daily_gains = [result['daily_gain'] for result in daily_results]
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total days analyzed: {len(daily_results)}")
    print(f"Worst floating negative balance: ${min(max_floating_balances):,.2f}")
    print(f"Best floating negative balance: ${max(max_floating_balances):,.2f}")
    print(f"Average floating negative balance: ${np.mean(max_floating_balances):,.2f}")
    print(f"Total gain/loss across all days: ${sum(daily_gains):,.2f}")
    print(f"Average daily gain/loss: ${np.mean(daily_gains):,.2f}")
    
    # Find the worst day
    worst_day_idx = max_floating_balances.index(min(max_floating_balances))
    worst_day = daily_results[worst_day_idx]
    print(f"\nWorst day: {worst_day['date']} ({worst_day['filename']})")
    print(f"  Max floating negative balance: ${worst_day['max_floating_negative_balance']:,.2f}")
    print(f"  Daily gain/loss: ${worst_day['daily_gain']:,.2f}")
    print(f"  Time of max floating loss: {worst_day['max_floating_timestamp'].strftime('%H:%M:%S %Z')}")
    
    print("="*80)


def main():
    """Main function to run the daily equity analysis"""
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description='Daily Equity Analyzer - Analyze maximum floating negative balance across multiple CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dailyEquityAnalyzer.py "C:\\path\\to\\csv\\files"
  python dailyEquityAnalyzer.py "C:\\Users\\maste\\OneDrive\\Documentos\\archived_logs\\xau-5-minutes-with-monitor"
  python dailyEquityAnalyzer.py "C:\\Users\\maste\\OneDrive\\Documentos\\archived_logs\\another-directory" --output-prefix "strategy2"
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        help='Directory path containing CSV files to analyze (use --list-dirs to see available directories)'
    )
    
    parser.add_argument(
        '--list-dirs',
        action='store_true',
        help='Show available directories in archived_logs and exit'
    )
    
    parser.add_argument(
        '--output-prefix',
        default='daily_equity_analysis',
        help='Prefix for output files (default: daily_equity_analysis)'
    )
    
    parser.add_argument(
        '--no-chart',
        action='store_true',
        help='Skip generating the chart visualization'
    )
    
    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='Skip saving detailed results to CSV'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle --list-dirs option
    if args.list_dirs:
        show_available_directories()
        sys.exit(0)
    
    # Check if directory argument was provided
    if not args.directory:
        print("Error: Directory path is required.")
        print("\nUse --help for usage information or --list-dirs to see available directories.")
        show_available_directories()
        sys.exit(1)
    
    # Get the CSV directory from command line argument
    csv_directory = args.directory
    
    # Validate directory exists
    if not os.path.exists(csv_directory):
        print(f"Error: Directory '{csv_directory}' does not exist.")
        show_available_directories()
        sys.exit(1)
    
    if not os.path.isdir(csv_directory):
        print(f"Error: '{csv_directory}' is not a directory.")
        sys.exit(1)
    
    print("Daily Equity Analyzer - Processing Multiple CSV Files")
    print("="*60)
    print(f"Looking for CSV files in: {csv_directory}")
    
    # Process all CSV files
    daily_results = process_all_csv_files(csv_directory)
    
    if not daily_results:
        print("No data processed. Exiting.")
        return
    
    # Print summary statistics
    print_summary_statistics(daily_results)
    
    # Create visualization (if not disabled)
    if not args.no_chart:
        print("\nGenerating visualization...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = os.path.join(os.path.dirname(__file__), f"{args.output_prefix}_{timestamp}.png")
        plot_daily_max_floating_balances(daily_results, save_path)
    else:
        print("\nSkipping chart generation (--no-chart flag used)")
    
    # Save detailed results to CSV (if not disabled)
    if not args.no_csv:
        results_df = pd.DataFrame(daily_results)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_csv_path = os.path.join(os.path.dirname(__file__), f"{args.output_prefix}_results_{timestamp}.csv")
        results_df.to_csv(results_csv_path, index=False)
        print(f"\nDetailed results saved to: {results_csv_path}")
    else:
        print("\nSkipping CSV export (--no-csv flag used)")


if __name__ == "__main__":
    main()