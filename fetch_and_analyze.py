import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# API configuration - England influenza hospital admission rate (weekly)
BASE_URL = "https://api.ukhsa-dashboard.data.gov.uk"
THEME = "infectious_disease"
SUB_THEME = "respiratory"
TOPIC = "Influenza"          # Exact topic name
GEOGRAPHY_TYPE = "Nation"    # Geography type
GEOGRAPHY = "England"        # Specific geography
METRIC = "influenza_healthcare_hospitalAdmissionRateByWeek"  # Exact metric name

def fetch_flu_data():
    url = f"{BASE_URL}/themes/{THEME}/sub_themes/{SUB_THEME}/topics/{TOPIC}/geography_types/{GEOGRAPHY_TYPE}/geographies/{GEOGRAPHY}/metrics/{METRIC}"
    data = []
    params = {"page_size": 500}

    while url:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            break

        json_data = response.json()
        results = json_data.get("results", [])
        if not results:
            print("No data returned for this metric.")
            break

        data.extend(results)
        url = json_data.get("next")
        params = {}  # Clear params after first page

    print(f"Fetched {len(data)} data points for flu hospital admissions.")
    return data

def process_data(raw_data):
    if not raw_data:
        return None

    df = pd.DataFrame(raw_data)

    # Debug: show structure
    print("Available columns:", df.columns.tolist())
    print("Sample row:\n", df.iloc[0] if not df.empty else "Empty")

    # Find the value column dynamically
    value_key = None
    for possible in ['metric_value', 'value', 'metricValue']:
        if possible in df.columns:
            value_key = possible
            break

    if value_key is None:
        print("Error: No value column found!")
        return None

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df = df.rename(columns={value_key: 'value'})

    # Analysis
    df['rolling_7_week_avg'] = df['value'].rolling(window=7).mean()

    # Seasonal labelling: flu season runs Oct–Sep
    df['month'] = df['date'].dt.month
    df['season_year'] = df['date'].dt.year
    df.loc[df['month'] >= 10, 'season_year'] += 1
    df['season_label'] = (df['season_year'] - 1).astype(str) + '-' + df['season_year'].astype(str).str[2:]

    df['week'] = df['date'].dt.isocalendar().week

    # filter to recent seasons for cleaner plots
    # df = df[df['season_year'] >= 2023]

    df.to_csv('flu_data.csv', index=False)
    print("Data saved to flu_data.csv")
    return df

def plot_time_series(df):
    plt.figure(figsize=(14, 7))
    sns.set_style("whitegrid")
    sns.lineplot(data=df, x='date', y='value', label='Weekly Admission Rate', color='steelblue')
    sns.lineplot(data=df, x='date', y='rolling_7_week_avg', label='7-Week Rolling Average', color='orange', linewidth=2)
    plt.title('England Influenza Hospital Admission Rate per 100,000\n(SARI-Watch Sentinel Data)')
    plt.xlabel('Date')
    plt.ylabel('Rate per 100,000')
    plt.legend()
    plt.tight_layout()
    plt.savefig('flu_trends.png')
    plt.show()
    print("Time series plot saved to flu_trends.png")

def plot_seasonal_comparison(df):
    plt.figure(figsize=(16, 8))
    sns.set_style("whitegrid")

    seasons = sorted(df['season_label'].unique())
    palette = sns.color_palette("husl", len(seasons))

    for i, season in enumerate(seasons):
        season_data = df[df['season_label'] == season]
        color = 'red' if season == max(seasons) else palette[i]
        linewidth = 4 if season == max(seasons) else 2
        label = f'{season} (current)' if season == max(seasons) else season
        sns.lineplot(data=season_data, x='week', y='value', label=label, color=color, linewidth=linewidth)

    # Current season rolling average
    current = df[df['season_label'] == max(seasons)]
    sns.lineplot(data=current, x='week', y='rolling_7_week_avg', color='darkred', linewidth=2, linestyle='--', label=f'{max(seasons)} 7-week avg')

    plt.title('England Influenza Hospital Admissions: Seasonal Comparison by Week\n(SARI-Watch | Week 40 ≈ October start)')
    plt.xlabel('ISO Week Number')
    plt.ylabel('Admission Rate per 100,000')
    plt.xlim(35, 52)  # Focus on main flu season
    plt.legend(title='Season')
    plt.tight_layout()
    plt.savefig('flu_seasonal_comparison.png')
    plt.show()
    print("Seasonal comparison plot saved to flu_seasonal_comparison.png")

if __name__ == "__main__":
    print("Fetching UK flu hospital admission data...")
    raw_data = fetch_flu_data()

    if raw_data:
        df = process_data(raw_data)
        if df is not None:
            plot_time_series(df)
            plot_seasonal_comparison(df)

            # Latest value
            current_season = df['season_label'].max()
            latest = df[df['season_label'] == current_season].iloc[-1]
            print(f"\nLatest data ({latest['date'].date()}, week {int(latest['week'])}): {latest['value']:.2f} per 100,000")
    else:
        print("No data fetched. Check internet or API status.")