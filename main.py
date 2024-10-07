import requests
import pandas as pd
from io import StringIO
import plotext as plt
from time import sleep
import argparse
import os
import platform

def console_clear():
    os.system("cls" if platform.system() == "Windows" else "clear")

def print_title():
    title_parts = [\
'''                                       ______                           _     ''',
'''      /\                              |  ____|                         | |    ''',
'''     /  \  _   _ _ __ ___  _ __ __ _  | |__ ___  _ __ ___  ___ __ _ ___| |_   ''',
'''    / /\ \| | | | '__/ _ \| '__/ _` | |  __/ _ \| '__/ _ \/ __/ _` / __| __|  ''',
'''   / ____ \ |_| | | | (_) | | | (_| | | | | (_) | | |  __/ (_| (_| \__ \ |_ _ ''',
'''  /_/    \_\__,_|_|  \___/|_|  \__,_| |_|  \___/|_|  \___|\___\__,_|___/\__(_)''',
    ]
    for part in title_parts:
        color = "red" if title_parts.index(part) < 3 else "green"
        print(plt.colorize(part, color, "bold"))

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        exit()

def process_data(data, utc_offset):
    lines = data.splitlines()
    filtered_lines = [line for line in lines if line and not line.startswith('#')]
    df = pd.read_csv(StringIO("\n".join(filtered_lines)), sep='\s+', header=None)
    df.columns = ['Observation', 'Forecast', 'North', 'South']
    # String date to datetime value
    df['Forecast'] = pd.to_datetime(df['Forecast'], format='%Y-%m-%d_%H:%M', errors='coerce')
    
    # UTC offset
    df['Forecast'] = df['Forecast'].dt.tz_localize('UTC', ambiguous='NaT')
    time_offset = pd.Timedelta(hours=utc_offset)
    df['Forecast'] = df['Forecast'] + time_offset
    return df


def plot_data(df, utc_offset):
    forecast_dates = df['Forecast'].dt.strftime(r'%Y/%m/%d %H:%M').tolist()
    north_values = df['North'].tolist()
    south_values = df['South'].tolist()

    if len(forecast_dates) != len(north_values) or len(forecast_dates) != len(south_values):
        raise ValueError("Dates and values must be the same length. Data error.")

    plt.clf()
    plt.date_form('Y/m/d H:M')
    title = f"Hemispheric-Power-Index in GW for UTC{'+' if utc_offset >= 0 else ''}{utc_offset}"

    if not args.no_north and not args.no_south:
        plt.simple_multiple_bar(forecast_dates, [north_values, south_values], width=80, labels=['North', 'South'], colors=['blue', 'orange'], title=plt.colorize(title, "white", "bold", "opacity", False), marker='━')
    elif not args.no_north:
        plt.simple_bar(forecast_dates, north_values, width=80, color='blue', title=plt.colorize(title + ". North", "white", "bold", "opacity", False), marker='━')
    elif not args.no_south:
        plt.simple_bar(forecast_dates, south_values, width=80, color='orange', title=plt.colorize(title + ". South", "white", "bold", "opacity", False), marker='━')
    else:
        print("You can't show ONLY south and ONLY north at the same time.\nSee command --help")
        exit()

def main():
    url = "https://services.swpc.noaa.gov/text/aurora-nowcast-hemi-power.txt"

    # Download and process data
    data = fetch_data(url)
    df = process_data(data, args.utc)

    # Tail last lines
    df = df.tail(args.lines)

    # Plot data
    plot_data(df, args.utc)

    # Clear screen if monitoring mode
    if args.monitoring:
        console_clear()

    # Print title program
    if not args.no_title:
        print_title()

    # Show plot
    plt.show()

    # Print your system time and refresh rate if monitoring mode is enabled
    your_time_now = pd.Timestamp.utcnow() + pd.Timedelta(hours=args.utc)
    print(f"Time now: {your_time_now.strftime('%Y/%m/%d %H:%M:%S')}")
    if args.monitoring:
        print(f"Update every {args.sleep} sec.")

if __name__ == "__main__":
    # Program options
    parser = argparse.ArgumentParser(description="Aurora forecast program.")
    parser.add_argument("-u", "--utc", type=int, default=0, help="UTC[NUM] location. Default 0.")
    parser.add_argument("-n", "--lines", type=int, default=10, help="Output the last num lines. Default 10.")
    parser.add_argument("-t", "--no-title", action='store_true', help="Disable program title. Default disable.")
    parser.add_argument("-m", "--monitoring", action='store_true', help="Enable monitoring mode. Default disable.")
    parser.add_argument("-s", "--sleep", type=int, default=15, help="Sleep seconds for monitoring mode. Default 15.")
    parser.add_argument("-S", "--no-north", action='store_true', help="Disable North information.")
    parser.add_argument("-N", "--no-south", action='store_true', help="Disable South information.")

    # Add options in args value
    args = parser.parse_args()

    try:
        # Run once or in monitoring mode
        if not args.monitoring:
            main()
            print()
            exit()

        # Monitoring mode
        while True:
            main()
            sleep(args.sleep)

    except KeyboardInterrupt:
        print("\nExit.")
