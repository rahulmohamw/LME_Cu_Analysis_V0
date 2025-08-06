# LME Copper Price Analysis Tool 🔧📊

A comprehensive Python-based analysis tool for London Metal Exchange (LME) Copper historical data, designed to identify optimal pricing strategies and beat monthly average prices.

## 🎯 Features

- **Historical Data Analysis**: Process years of LME copper price data
- **Pricing Strategy Optimization**: Identify the best days, weeks, and strategies to price copper
- **Interactive Dashboard**: Web-based visualization of analysis results
- **Automated Scheduling**: Daily analysis runs at configured times
- **Performance Tracking**: Compare daily rates against monthly averages
- **Risk Assessment**: Evaluate different pricing strategies with risk levels

## 📁 Repository Structure

```
lme-copper-analysis/
│
├── data/                           # Data directory
│   └── lme_copper_historical_data.csv
│
├── output/                         # Analysis outputs
│   ├── analysis_results.json      # Latest analysis
│   └── backups/                   # Historical analysis backups
│
├── copper_analysis.py             # Main analysis engine
├── copper_dashboard.html          # Interactive web dashboard
├── analysis_results.json          # Latest results (for dashboard)
├── requirements.txt               # Python dependencies
├── run_analysis.sh               # Linux/Mac automation script
├── run_analysis.bat              # Windows automation script
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lme-copper-analysis.git
cd lme-copper-analysis
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare Your Data

Place your LME copper historical data CSV file in the `data/` directory:
```bash
cp your_copper_data.csv data/lme_copper_historical_data.csv
```

Expected CSV format:
- `date`: Date column (MM/DD/YYYY or YYYY-MM-DD)
- `lme_copper_cash_settlement`: Cash settlement price
- `lme_copper_3_month`: 3-month price (optional)
- `lme_copper_stock`: Stock levels (optional)

### 4. Run Analysis

```bash
# Analyze all available data
python copper_analysis.py

# Analyze specific date range
python copper_analysis.py 2024-01-01 2024-12-31
```

### 5. View Results

Open `copper_dashboard.html` in your web browser to view the interactive dashboard.

## 📊 Analysis Outputs

The tool provides comprehensive insights including:

### **Pricing Strategies**
- **Single Day Strategy**: Price 100% on the historically best performing day
- **Two-Day Split**: Distribute 50% each on top 2 performing days
- **Week-Focused**: Concentrate 70% in the best performing week
- **Risk Avoidance**: Avoid historically worst performing days

### **Performance Metrics**
- Expected performance vs monthly average (%)
- Historical success rate
- Risk level assessment (High/Medium/Low)
- Volatility analysis

### **Temporal Patterns**
- Best day of the week for pricing
- Optimal week of the month
- Monthly seasonality trends
- Year-over-year growth patterns

## 🔄 Automated Scheduling

### Linux/Mac (using cron)

1. Make the script executable:
```bash
chmod +x run_analysis.sh
```

2. Add to crontab for daily 7:30 PM execution:
```bash
crontab -e
# Add this line:
30 19 * * * /path/to/lme-copper-analysis/run_analysis.sh
```

### Windows (using Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 7:30 PM
4. Set action: Start `run_analysis.bat`
5. Set working directory to repository path

### Python Scheduler (Platform Independent)

Run the built-in scheduler:
```bash
python copper_analysis.py --schedule
```

## 📈 Dashboard Features

The interactive HTML dashboard provides:

- **Real-time Data Visualization**: Charts using Chart.js
- **Period Selection**: Analyze custom date ranges
- **Multiple Views**:
  - Pricing strategies comparison
  - Weekly performance patterns
  - Monthly trends
  - Day-of-week analysis
- **Key Performance Indicators**: At-a-glance metrics
- **Responsive Design**: Works on desktop and mobile

## 🛠️ Configuration

### Modifying Analysis Parameters

Edit `copper_analysis.py` to adjust:
- Analysis period defaults
- Strategy percentages
- Risk thresholds
- Moving average windows

### Custom Data Sources

To use a different CSV filename, modify in `copper_analysis.py`:
```python
analyzer = CopperLMEAnalyzer('your_custom_file.csv')
```

## 📝 API Usage

### Python Module

```python
from copper_analysis import CopperLMEAnalyzer

# Initialize analyzer
analyzer = CopperLMEAnalyzer()

# Run analysis
results = analyzer.run_analysis('2024-01-01', '2024-12-31')

# Access specific metrics
monthly_patterns = results['monthly_analysis']
best_strategy = results['pricing_strategy'][0]
```

### JSON Output Structure

```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-12-31",
    "total_days": 250
  },
  "overall_stats": {
    "mean": 9500.50,
    "median": 9450.00,
    "std": 350.25
  },
  "pricing_strategy": [...],
  "weekly_patterns": [...],
  "monthly_analysis": [...],
  "trends": {...}
}
```

## 🔍 Advanced Analysis

### Custom Strategies

Add custom pricing strategies by extending the `_calculate_pricing_strategy` method:

```python
def custom_strategy(self, df):
    # Your custom logic here
    return strategy_results
```

### Additional Metrics

Extend the analyzer with new metrics:

```python
def _analyze_custom_metric(self, df):
    # Custom analysis logic
    return metric_results
```

## 📊 Sample Results

Example strategy performance:
- **Tuesday-Thursday Split**: +2.3% vs monthly average, 73% success rate
- **Week 2 Focus**: +1.8% vs monthly average, 68% success rate
- **Avoid Mondays**: +0.9% vs monthly average, 61% success rate

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**Issue**: "FileNotFoundError: data/lme_copper_historical_data.csv"
- **Solution**: Ensure your CSV file is in the `data/` directory

**Issue**: Analysis results not showing in dashboard
- **Solution**: Check that `analysis_results.json` exists in the root directory

**Issue**: Schedule not running
- **Solution**: Verify cron/Task Scheduler configuration and Python path

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

## 🚦 System Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 4GB RAM minimum
- 100MB free disk space

## 🔄 Update History

- **v1.0.0** - Initial release with core analysis features
- **v1.1.0** - Added interactive dashboard
- **v1.2.0** - Implemented automated scheduling
- **v1.3.0** - Enhanced strategy recommendations

---

**Built with ❤️ for optimal copper pricing strategies**