# Equity Analyzer

A Python-based tool for analyzing MetaTrader 4 (MT4) equity data and visualizing trading performance through comprehensive charts.

## Overview

This tool processes equity log data from MT4 trading sessions and generates detailed visualizations showing:
- Equity and balance trends over time
- Maximum and minimum equity points with timestamps
- Drawdown analysis throughout the trading period

## Requirements

- Python 3.x
- pandas
- matplotlib
- numpy

## Installation

1. Install the required Python packages:
```bash
pip install pandas matplotlib numpy
```

## Usage

### 1. Prepare Your Data

The analyzer expects a CSV file named `EquityLogClean.csv` with the following format:
- **Delimiter**: Semicolon (`;`)
- **Columns** (no headers):
  1. Timestamp (format: `YYYY.MM.DD HH:MM:SS`)
  2. Equity value
  3. Balance value
  4. Drawdown percentage

Example data format:
```
2025.09.16 17:59:25;2925.82;2928.54;0
2025.09.16 17:59:26;2925.6;2928.54;0.007519259558012955
2025.09.16 17:59:27;2926.15;2928.54;0
```

### 2. Run the Analyzer

1. Place your `EquityLogClean.csv` file in the `python/` directory
2. Navigate to the `python/` directory:
   ```bash
   cd python
   ```
3. Run the analyzer:
   ```bash
   python equityAnalizer.py
   ```

### 3. Output

The tool will generate a comprehensive visualization with three main sections:

1. **Left Panel**: Bar chart showing highest and lowest equity points with exact timestamps
2. **Top Right Panel**: Line chart comparing equity vs balance over time
3. **Bottom Right Panel**: Drawdown analysis over time

The charts will display in a new window using matplotlib's interactive viewer.

## File Structure

```
equityanalizer/
├── python/
│   ├── equityAnalizer.py      # Main analysis script
│   ├── EquityLogClean.csv     # Your equity data (place here)
│   └── .gitignore             # Git ignore file
└── README.md                  # This file
```

## Features

- **Automatic Data Processing**: Handles timestamp parsing and data formatting
- **Multi-Panel Visualization**: Three synchronized charts for comprehensive analysis
- **Extreme Values Identification**: Automatically identifies and displays maximum/minimum equity points
- **Time-Series Analysis**: Shows trends over your complete trading session
- **Drawdown Tracking**: Visualizes risk exposure throughout the trading period

## Data Source

This tool is designed to work with equity logs exported from MetaTrader 4 (MT4) trading platform. Ensure your data follows the expected semicolon-delimited format for proper analysis.

## Notes

- The script looks for `EquityLogClean.csv` in the same directory as the Python file
- All timestamps should be in `YYYY.MM.DD HH:MM:SS` format
- The tool displays interactive charts using matplotlib - you can zoom, pan, and save the visualizations
- Drawdown values should be in decimal format (e.g., 0.05 for 5% drawdown)