#!/usr/bin/env python3
"""
LME Copper Historical Data Analysis Tool
Analyzes copper cash settlement prices to identify optimal pricing strategies
GitHub Repository Version
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings
import schedule
import time
import os
import sys
from pathlib import Path

warnings.filterwarnings('ignore')

# Repository structure paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'
BACKUP_DIR = OUTPUT_DIR / 'backups'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

class CopperLMEAnalyzer:
    def __init__(self, csv_filename='lme_copper_historical_data.csv'):
        """Initialize the analyzer with the CSV file path"""
        self.csv_path = DATA_DIR / csv_filename
        self.df = None
        self.analysis_results = {}
        
    def load_data(self):
        """Load and preprocess the CSV data"""
        try:
            # Read CSV
            self.df = pd.read_csv(self.csv_path)
            
            # Parse dates with multiple format support
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce', dayfirst=False)
            
            # Sort by date
            self.df = self.df.sort_values('date')
            
            # Remove rows with null cash settlement values
            self.df = self.df[self.df['lme_copper_cash_settlement'].notna()]
            
            # Add time-based features
            self.df['year'] = self.df['date'].dt.year
            self.df['month'] = self.df['date'].dt.month
            self.df['month_name'] = self.df['date'].dt.strftime('%B')
            self.df['day'] = self.df['date'].dt.day
            self.df['weekday'] = self.df['date'].dt.dayofweek
            self.df['weekday_name'] = self.df['date'].dt.strftime('%A')
            self.df['week_of_month'] = self.df['date'].apply(self._get_week_of_month)
            self.df['quarter'] = self.df['date'].dt.quarter
            
            print(f"Data loaded successfully: {len(self.df)} records from {self.df['date'].min().date()} to {self.df['date'].max().date()}")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def _get_week_of_month(self, date):
        """Calculate week of month (1-5)"""
        first_day = date.replace(day=1)
        adjusted_day = date.day + first_day.weekday()
        return (adjusted_day - 1) // 7 + 1
    
    def analyze_period(self, start_date=None, end_date=None):
        """Analyze data for a specific period"""
        if start_date is None:
            start_date = self.df['date'].min()
        else:
            start_date = pd.to_datetime(start_date)
            
        if end_date is None:
            end_date = self.df['date'].max()
        else:
            end_date = pd.to_datetime(end_date)
        
        # Filter data for the period
        period_df = self.df[(self.df['date'] >= start_date) & (self.df['date'] <= end_date)].copy()
        
        if len(period_df) == 0:
            return {"error": "No data available for the selected period"}
        
        results = {
            "period": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d'),
                "total_days": len(period_df)
            }
        }
        
        # Overall statistics
        results["overall_stats"] = self._calculate_overall_stats(period_df)
        
        # Monthly analysis
        results["monthly_analysis"] = self._analyze_monthly_patterns(period_df)
        
        # Weekly patterns within month
        results["weekly_patterns"] = self._analyze_weekly_patterns(period_df)
        
        # Best day of week analysis
        results["weekday_analysis"] = self._analyze_weekday_patterns(period_df)
        
        # Pricing strategy recommendations
        results["pricing_strategy"] = self._calculate_pricing_strategy(period_df)
        
        # Trend and seasonality
        results["trends"] = self._analyze_trends(period_df)
        
        # Volatility analysis
        results["volatility"] = self._analyze_volatility(period_df)
        
        return results
    
    def _calculate_overall_stats(self, df):
        """Calculate overall statistics"""
        return {
            "mean": float(df['lme_copper_cash_settlement'].mean()),
            "median": float(df['lme_copper_cash_settlement'].median()),
            "std": float(df['lme_copper_cash_settlement'].std()),
            "min": float(df['lme_copper_cash_settlement'].min()),
            "max": float(df['lme_copper_cash_settlement'].max()),
            "range": float(df['lme_copper_cash_settlement'].max() - df['lme_copper_cash_settlement'].min())
        }
    
    def _analyze_monthly_patterns(self, df):
        """Analyze monthly patterns and compare daily rates to monthly averages"""
        monthly_stats = []
        
        for (year, month), month_df in df.groupby(['year', 'month']):
            month_avg = month_df['lme_copper_cash_settlement'].mean()
            
            # Calculate how many days beat the monthly average
            days_above_avg = (month_df['lme_copper_cash_settlement'] > month_avg).sum()
            days_below_avg = (month_df['lme_copper_cash_settlement'] <= month_avg).sum()
            
            # Best and worst days in the month
            best_day = month_df.loc[month_df['lme_copper_cash_settlement'].idxmax()]
            worst_day = month_df.loc[month_df['lme_copper_cash_settlement'].idxmin()]
            
            monthly_stats.append({
                "year": int(year),
                "month": int(month),
                "month_name": month_df['month_name'].iloc[0],
                "average": float(month_avg),
                "min": float(month_df['lme_copper_cash_settlement'].min()),
                "max": float(month_df['lme_copper_cash_settlement'].max()),
                "std": float(month_df['lme_copper_cash_settlement'].std()),
                "days_above_average": int(days_above_avg),
                "days_below_average": int(days_below_avg),
                "best_day": {
                    "date": best_day['date'].strftime('%Y-%m-%d'),
                    "value": float(best_day['lme_copper_cash_settlement']),
                    "premium_to_avg": float(best_day['lme_copper_cash_settlement'] - month_avg)
                },
                "worst_day": {
                    "date": worst_day['date'].strftime('%Y-%m-%d'),
                    "value": float(worst_day['lme_copper_cash_settlement']),
                    "discount_to_avg": float(month_avg - worst_day['lme_copper_cash_settlement'])
                }
            })
        
        # Calculate month-of-year seasonality
        month_seasonality = df.groupby('month')['lme_copper_cash_settlement'].agg(['mean', 'std']).reset_index()
        month_seasonality['month_name'] = month_seasonality['month'].apply(lambda x: pd.Timestamp(2024, x, 1).strftime('%B'))
        
        return {
            "monthly_details": monthly_stats,
            "seasonality": month_seasonality.to_dict('records')
        }
    
    def _analyze_weekly_patterns(self, df):
        """Analyze patterns by week of month"""
        weekly_stats = []
        
        for week in range(1, 6):
            week_df = df[df['week_of_month'] == week]
            if len(week_df) > 0:
                # Calculate performance vs monthly average
                performance_vs_month = []
                for (year, month), group in week_df.groupby(['year', 'month']):
                    month_avg = df[(df['year'] == year) & (df['month'] == month)]['lme_copper_cash_settlement'].mean()
                    week_avg = group['lme_copper_cash_settlement'].mean()
                    performance_vs_month.append((week_avg / month_avg - 1) * 100)
                
                weekly_stats.append({
                    "week": f"Week {week}",
                    "avg_price": float(week_df['lme_copper_cash_settlement'].mean()),
                    "std": float(week_df['lme_copper_cash_settlement'].std()),
                    "count": len(week_df),
                    "avg_performance_vs_month": float(np.mean(performance_vs_month)) if performance_vs_month else 0,
                    "best_performance": float(np.max(performance_vs_month)) if performance_vs_month else 0,
                    "worst_performance": float(np.min(performance_vs_month)) if performance_vs_month else 0
                })
        
        # Rank weeks by average performance
        weekly_stats.sort(key=lambda x: x['avg_performance_vs_month'], reverse=True)
        
        return weekly_stats
    
    def _analyze_weekday_patterns(self, df):
        """Analyze patterns by day of week"""
        weekday_stats = []
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in range(7):
            day_df = df[df['weekday'] == day]
            if len(day_df) > 0:
                # Calculate how often this day beats the monthly average
                beats_monthly_avg = 0
                total_comparisons = 0
                
                for (year, month), group in day_df.groupby(['year', 'month']):
                    month_avg = df[(df['year'] == year) & (df['month'] == month)]['lme_copper_cash_settlement'].mean()
                    beats_monthly_avg += (group['lme_copper_cash_settlement'] > month_avg).sum()
                    total_comparisons += len(group)
                
                weekday_stats.append({
                    "weekday": weekday_names[day],
                    "avg_price": float(day_df['lme_copper_cash_settlement'].mean()),
                    "std": float(day_df['lme_copper_cash_settlement'].std()),
                    "count": len(day_df),
                    "beats_monthly_avg_pct": float(beats_monthly_avg / total_comparisons * 100) if total_comparisons > 0 else 0
                })
        
        # Rank days by performance
        weekday_stats.sort(key=lambda x: x['beats_monthly_avg_pct'], reverse=True)
        
        return weekday_stats
    
    def _calculate_pricing_strategy(self, df):
        """Calculate optimal pricing strategies"""
        strategies = []
        
        # Strategy 1: Price everything on best day of week
        best_day = df.groupby('weekday')['lme_copper_cash_settlement'].mean().idxmax()
        best_day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][best_day]
        best_day_df = df[df['weekday'] == best_day]
        
        strategy1_performance = []
        for (year, month), group in best_day_df.groupby(['year', 'month']):
            month_avg = df[(df['year'] == year) & (df['month'] == month)]['lme_copper_cash_settlement'].mean()
            if len(group) > 0:
                strategy1_performance.append((group['lme_copper_cash_settlement'].mean() / month_avg - 1) * 100)
        
        strategies.append({
            "name": f"Single Day Strategy (All on {best_day_name})",
            "description": f"Price 100% of quantity on {best_day_name}",
            "avg_performance_vs_monthly": float(np.mean(strategy1_performance)) if strategy1_performance else 0,
            "success_rate": float(sum(p > 0 for p in strategy1_performance) / len(strategy1_performance) * 100) if strategy1_performance else 0,
            "risk_level": "High"
        })
        
        # Strategy 2: Spread across best 2 days
        best_2_days = df.groupby('weekday')['lme_copper_cash_settlement'].mean().nlargest(2).index.tolist()
        best_2_names = [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][d] for d in best_2_days]
        best_2_df = df[df['weekday'].isin(best_2_days)]
        
        strategy2_performance = []
        for (year, month), group in best_2_df.groupby(['year', 'month']):
            month_avg = df[(df['year'] == year) & (df['month'] == month)]['lme_copper_cash_settlement'].mean()
            if len(group) > 0:
                strategy2_performance.append((group['lme_copper_cash_settlement'].mean() / month_avg - 1) * 100)
        
        strategies.append({
            "name": f"Two-Day Split Strategy ({', '.join(best_2_names)})",
            "description": f"Price 50% each on {' and '.join(best_2_names)}",
            "avg_performance_vs_monthly": float(np.mean(strategy2_performance)) if strategy2_performance else 0,
            "success_rate": float(sum(p > 0 for p in strategy2_performance) / len(strategy2_performance) * 100) if strategy2_performance else 0,
            "risk_level": "Medium"
        })
        
        # Strategy 3: Week-based strategy
        best_week = df.groupby('week_of_month')['lme_copper_cash_settlement'].mean().idxmax()
        best_week_df = df[df['week_of_month'] == best_week]
        
        strategy3_performance = []
        for (year, month), group in best_week_df.groupby(['year', 'month']):
            month_avg = df[(df['year'] == year) & (df['month'] == month)]['lme_copper_cash_settlement'].mean()
            if len(group) > 0:
                strategy3_performance.append((group['lme_copper_cash_settlement'].mean() / month_avg - 1) * 100)
        
        strategies.append({
            "name": f"Week {best_week} Focus Strategy",
            "description": f"Price 70% in Week {best_week}, 30% spread across other weeks",
            "avg_performance_vs_monthly": float(np.mean(strategy3_performance) * 0.7) if strategy3_performance else 0,
            "success_rate": float(sum(p > 0 for p in strategy3_performance) / len(strategy3_performance) * 100) if strategy3_performance else 0,
            "risk_level": "Medium"
        })
        
        # Strategy 4: Avoid worst days
        worst_day = df.groupby('weekday')['lme_copper_cash_settlement'].mean().idxmin()
        avoid_day_df = df[df['weekday'] != worst_day]
        
        strategy4_performance = []
        for (year, month), group in avoid_day_df.groupby(['year', 'month']):
            month_avg = df[(df['year'] == year) & (df['month'] == month)]['lme_copper_cash_settlement'].mean()
            if len(group) > 0:
                strategy4_performance.append((group['lme_copper_cash_settlement'].mean() / month_avg - 1) * 100)
        
        worst_day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][worst_day]
        strategies.append({
            "name": f"Avoid {worst_day_name} Strategy",
            "description": f"Spread pricing equally across all days except {worst_day_name}",
            "avg_performance_vs_monthly": float(np.mean(strategy4_performance)) if strategy4_performance else 0,
            "success_rate": float(sum(p > 0 for p in strategy4_performance) / len(strategy4_performance) * 100) if strategy4_performance else 0,
            "risk_level": "Low"
        })
        
        # Sort strategies by performance
        strategies.sort(key=lambda x: x['avg_performance_vs_monthly'], reverse=True)
        
        return strategies
    
    def _analyze_trends(self, df):
        """Analyze price trends and cycles"""
        # Calculate moving averages
        df_sorted = df.sort_values('date').copy()
        df_sorted['ma_7'] = df_sorted['lme_copper_cash_settlement'].rolling(window=7, min_periods=1).mean()
        df_sorted['ma_30'] = df_sorted['lme_copper_cash_settlement'].rolling(window=30, min_periods=1).mean()
        df_sorted['ma_90'] = df_sorted['lme_copper_cash_settlement'].rolling(window=90, min_periods=1).mean()
        
        # Trend direction
        recent_trend = "Upward" if df_sorted['ma_30'].iloc[-1] > df_sorted['ma_30'].iloc[-30] else "Downward"
        
        # Calculate year-over-year growth
        yoy_growth = []
        for year in df['year'].unique():
            if year > df['year'].min():
                curr_year_avg = df[df['year'] == year]['lme_copper_cash_settlement'].mean()
                prev_year_avg = df[df['year'] == year - 1]['lme_copper_cash_settlement'].mean()
                yoy_growth.append({
                    "year": int(year),
                    "growth_pct": float((curr_year_avg / prev_year_avg - 1) * 100)
                })
        
        # Identify cycles (simplified approach using peak detection)
        from scipy.signal import find_peaks
        
        # Use monthly averages for cycle detection
        monthly_avg = df.groupby(['year', 'month'])['lme_copper_cash_settlement'].mean().values
        peaks, _ = find_peaks(monthly_avg, distance=3)
        troughs, _ = find_peaks(-monthly_avg, distance=3)
        
        avg_cycle_length = np.mean(np.diff(peaks)) if len(peaks) > 1 else 0
        
        return {
            "current_trend": recent_trend,
            "ma_7_current": float(df_sorted['ma_7'].iloc[-1]),
            "ma_30_current": float(df_sorted['ma_30'].iloc[-1]),
            "ma_90_current": float(df_sorted['ma_90'].iloc[-1]),
            "yoy_growth": yoy_growth,
            "cycle_info": {
                "peaks_detected": len(peaks),
                "troughs_detected": len(troughs),
                "avg_cycle_months": float(avg_cycle_length)
            }
        }
    
    def _analyze_volatility(self, df):
        """Analyze price volatility"""
        # Calculate daily returns
        df_sorted = df.sort_values('date').copy()
        df_sorted['daily_return'] = df_sorted['lme_copper_cash_settlement'].pct_change()
        
        # Monthly volatility
        monthly_vol = df.groupby(['year', 'month'])['lme_copper_cash_settlement'].std()
        
        # Volatility by day of week
        weekday_vol = df.groupby('weekday')['lme_copper_cash_settlement'].std()
        
        # Volatility by week of month
        week_vol = df.groupby('week_of_month')['lme_copper_cash_settlement'].std()
        
        return {
            "overall_volatility": float(df['lme_copper_cash_settlement'].std()),
            "daily_return_stats": {
                "mean": float(df_sorted['daily_return'].mean() * 100) if not df_sorted['daily_return'].isna().all() else 0,
                "std": float(df_sorted['daily_return'].std() * 100) if not df_sorted['daily_return'].isna().all() else 0,
                "max": float(df_sorted['daily_return'].max() * 100) if not df_sorted['daily_return'].isna().all() else 0,
                "min": float(df_sorted['daily_return'].min() * 100) if not df_sorted['daily_return'].isna().all() else 0
            },
            "most_volatile_month": int(monthly_vol.idxmax()[1]) if len(monthly_vol) > 0 else 0,
            "least_volatile_month": int(monthly_vol.idxmin()[1]) if len(monthly_vol) > 0 else 0,
            "most_volatile_weekday": int(weekday_vol.idxmax()) if len(weekday_vol) > 0 else 0,
            "most_volatile_week": int(week_vol.idxmax()) if len(week_vol) > 0 else 0
        }
    
    def save_results(self, results, output_filename='analysis_results.json'):
        """Save analysis results to JSON file"""
        output_path = OUTPUT_DIR / output_filename
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {output_path}")
        
        # Also save in root for HTML dashboard
        root_output = BASE_DIR / 'analysis_results.json'
        with open(root_output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Dashboard data saved to {root_output}")
    
    def run_analysis(self, start_date=None, end_date=None):
        """Main method to run the complete analysis"""
        if not self.load_data():
            return None
        
        results = self.analyze_period(start_date, end_date)
        
        # Add metadata
        results['metadata'] = {
            'analysis_timestamp': datetime.now().isoformat(),
            'data_source': self.csv_path,
            'total_records': len(self.df),
            'data_range': {
                'start': self.df['date'].min().strftime('%Y-%m-%d'),
                'end': self.df['date'].max().strftime('%Y-%m-%d')
            }
        }
        
        # Save results
        self.save_results(results)
        
        return results

def scheduled_analysis():
    """Function to run scheduled analysis"""
    print(f"Running scheduled analysis at {datetime.now()}")
    analyzer = CopperLMEAnalyzer()
    
    # Run analysis for the last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    results = analyzer.run_analysis(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    if results:
        print("Analysis completed successfully")
        # Also save a timestamped version in backups
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'analysis_results_{timestamp}.json'
        analyzer.save_results(results, backup_filename)
        
        # Save to backup directory
        backup_path = BACKUP_DIR / backup_filename
        with open(backup_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Backup saved to {backup_path}")

def main():
    """Main function with options for manual or scheduled runs"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        # Schedule the analysis to run daily at 7:30 PM
        schedule.every().day.at("19:30").do(scheduled_analysis)
        
        print("Scheduler started. Analysis will run daily at 7:30 PM")
        print("Press Ctrl+C to stop")
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    else:
        # Run analysis immediately
        analyzer = CopperLMEAnalyzer()
        
        # Check for command line arguments for date range
        if len(sys.argv) >= 3:
            start_date = sys.argv[1]
            end_date = sys.argv[2]
            print(f"Analyzing period from {start_date} to {end_date}")
            results = analyzer.run_analysis(start_date, end_date)
        else:
            print("Analyzing all available data")
            results = analyzer.run_analysis()
        
        if results:
            print("\n" + "="*60)
            print("ANALYSIS SUMMARY")
            print("="*60)
            
            # Print key insights
            if 'pricing_strategy' in results:
                print("\nTop Pricing Strategy:")
                top_strategy = results['pricing_strategy'][0]
                print(f"  {top_strategy['name']}")
                print(f"  Expected Performance vs Monthly Avg: {top_strategy['avg_performance_vs_monthly']:.2f}%")
                print(f"  Success Rate: {top_strategy['success_rate']:.1f}%")
            
            if 'weekday_analysis' in results:
                print("\nBest Day to Price:")
                best_day = results['weekday_analysis'][0]
                print(f"  {best_day['weekday']} - Beats monthly avg {best_day['beats_monthly_avg_pct']:.1f}% of the time")
            
            if 'weekly_patterns' in results:
                print("\nBest Week to Price:")
                best_week = results['weekly_patterns'][0]
                print(f"  {best_week['week']} - Avg performance vs month: {best_week['avg_performance_vs_month']:.2f}%")
            
            print("\nFull results saved to analysis_results.json")
            print("Open copper_dashboard.html in a browser to view the interactive dashboard")

if __name__ == "__main__":
    main()