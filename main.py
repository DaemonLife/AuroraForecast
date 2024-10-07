import requests
import pandas as pd
from io import StringIO
import plotext as plt
from time import sleep
import argparse
import os
import platform

def console_clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear") # UNIX like system

def print_title():
    str0 = '''                                      ______                           _     
     /\                              |  ____|                         | |    
'''
    str1 = '''   /  \  _   _ _ __ ___  _ __ __ _  | |__ ___  _ __ ___  ___ __ _ ___| |_   
   / /\ \| | | | '__/ _ \| '__/ _` | |  __/ _ \| '__/ _ \/ __/ _` / __| __|  
'''
    str2 = ''' / ____ \ |_| | | | (_) | | | (_| | | | | (_) | | |  __/ (_| (_| \__ \ |_ _ 
'''
    str3 = '''/_/    \_\__,_|_|  \___/|_|  \__,_| |_|  \___/|_|  \___|\___\__,_|___/\__(_)
'''
    print(plt.colorize(str0, "red", "bold"), end = ' ')
    print(plt.colorize(str1, "red", "bold"), end = ' ')
    print(plt.colorize(str2, "green", "bold"), end = ' ')
    print(plt.colorize(str3, "green", "bold"))

def main ():

    # Get UTC location
    UTC_correct = args.utc 

    # Download data
    response = requests.get(url)
    data = response.text

    # Split by lines and remove comments
    lines = data.splitlines()
    filtered_lines = [line for line in lines if line and not line.startswith('#')]

    # Write it pandas DataFrame (df)
    df = pd.read_csv(StringIO("\n".join(filtered_lines)), sep='\s+', header=None)

    # Give names to columns 
    df.columns = ['Observation', 'Forecast', 'North', 'South']

    # Format date text to datetime format
    df['Forecast'] = pd.to_datetime(df['Forecast'], format='%Y-%m-%d_%H:%M', errors='coerce')

    # Get current UTC time
    current_time_utc = pd.Timestamp.utcnow()

    # Localize Forecast column with datetime to UTC 
    df['Forecast'] = df['Forecast'].dt.tz_localize('UTC', ambiguous='NaT')
    
    # Tail last lines
    df = df.tail(args.lines) 

    # Make it your UTC+N time
    time_offset = pd.Timedelta(hours=UTC_correct, minutes=0)
    df['Forecast'] = df['Forecast'] + time_offset

    # Format datetime to string for plotext
    df['Forecast'] = df['Forecast'].dt.strftime(r'%Y/%m/%d %H:%M')

    # Plot setup
    forecast_dates = df['Forecast'].tolist()
    north_values = df['North'].tolist()
    south_values = df['South'].tolist()

    # Check if there is empty values in lists
    if len(forecast_dates) != len(north_values) != len(south_values):
        raise ValueError("Dates and values must be the same length. Data error.")

    plt.clf()  # Clear others plots
    plt.date_form('Y/m/d H:M') # Datetime format for plot
    # Correcting plot title with UTC
    if UTC_correct > 0:
        title = f"Hemispheric-Power-Index in GW for UTC+{UTC_correct}" 
    elif UTC_correct < 0:
        title = f"Hemispheric-Power-Index in GW for UTC{UTC_correct}" 
    else:
        title = f"Hemispheric-Power-Index in GW for UTC" 

    # Making plot (not showing yet)
    # North + South
    if (args.no_north == False) and (args.no_south == False):
        plt.simple_multiple_bar(forecast_dates, [north_values, south_values], width = 80, labels = ['North', 'South'], colors = ['blue', 'orange'], title = plt.colorize(title, "white", "bold", "opacity", False), marker='━')
    # Only North
    elif (args.no_north == False) and (args.no_south == True):
        plt.simple_bar(forecast_dates, north_values, width = 80, color = 'blue', title = plt.colorize(title + ". North", "white", "bold", "opacity", False), marker='━')
    # Only South
    elif (args.no_north == True) and (args.no_south == False):
        plt.simple_bar(forecast_dates, south_values, width = 80, color = 'orange', title = plt.colorize(title + ". South", "white", "bold", "opacity", False), marker='━')
    # Error
    else:
        print("You can't show ONLY south and ONLY north at the same time.\nSee command --help")
        exit()

    # Clear screen if monitoring mode
    if args.monitoring == True:
        console_clear()

    # Print title program
    if args.no_title != True: # if title is not disabled
        print_title()

    # And now show plot
    plt.show()
    
    # Print your system time and refresh rate if monitoring mode is enabled
    your_time_now = current_time_utc + time_offset
    print(f"Time now: {your_time_now.strftime('%Y/%m/%d %H:%M:%S')}")
    if args.monitoring == True:
        print(f"Update every {args.sleep} sec.")

if __name__ == "__main__":
    # Data url
    url = "https://services.swpc.noaa.gov/text/aurora-nowcast-hemi-power.txt"

    # Program options
    parser = argparse.ArgumentParser(description=f"Aurora forecast program.\nAll data from {url}")
    parser.add_argument("-u", "--utc", type = int, default = 0, help = "UTC[NUM] location. Default 0.")
    parser.add_argument("-n", "--lines", type = int, default = 10, help = "Output the last  num  lines. Default 10.")
    parser.add_argument("-t", "--no-title", action='store_true', help = "Disable program title. Default disable.")
    parser.add_argument("-m", "--monitoring", action='store_true', help = "Enable monitoring mode. Default disable.")
    parser.add_argument("-s", "--sleep", type = int, default = 15, help = "Sleep seconds for monitoring mode. Default 15.")
    parser.add_argument("-S", "--no-north", action='store_true', help = "Disable North information.")
    parser.add_argument("-N", "--no-south", action='store_true', help = "Disable South information.")

    # Add options in args value
    args = parser.parse_args()

    try: 
        # Run once
        if args.monitoring != True:
            main()
            print()
            exit()
        
        # Monitoring mode
        while True:
            main()
            sleep(args.sleep)
    
    # For ^C exit
    except KeyboardInterrupt: 
        print("\nExit.")
