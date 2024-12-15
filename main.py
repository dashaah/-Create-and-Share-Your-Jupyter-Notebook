import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as plt
import datetime

# Set up Chrome options to run headlessly (without opening a browser window)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in the background without opening a browser window
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional but recommended for headless)

# Set up the ChromeDriver using webdriver-manager
service = Service(ChromeDriverManager().install())

# Initialize WebDriver with the Service object and options
driver = webdriver.Chrome(service=service, options=chrome_options)

def hello_world(message):
    print(message)
    
hello_world("i like turtles")

# Function to fetch stock data
def fetch_stock_data(stock):
    #  URL to fetch the historical data for the stock
    url = f"https://finance.yahoo.com/quote/{stock}/history/"

    # Open the page
    driver.get(url)

    # Wait for the table to load
    try:
        # Wait until the <tbody> is present on the page (the body of the table)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//tbody"))
        )
        print("Table loaded successfully.")
    except Exception as e:
        print("Error loading table:")
        print(e)
        driver.quit()
        exit()

    # Get the page content after it's fully loaded
    page_content = driver.page_source

    # Parse the page with BeautifulSoup to extract the table
    soup = BeautifulSoup(page_content, 'html.parser')

    # Find the <tbody> which contains the rows we need
    table_body = soup.find('tbody')

    # Extract table rows (each row represents a stock entry)
    rows = table_body.find_all('tr')

    # Prepare a list to hold the scraped data
    data = []

    # Iterate through each row and extract the data
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 7:  # Ensure that there are enough columns (7 columns per row)
            date = cols[0].text.strip()
            open_price = cols[1].text.strip()
            high = cols[2].text.strip()
            low = cols[3].text.strip()
            close = cols[4].text.strip()
            adj_close = cols[5].text.strip()
            volume = cols[6].text.strip()

            # Add the row data to the data list as a dictionary
            data.append({
                "Date": date,
                "Open": open_price,
                "High": high,
                "Low": low,
                "Close": close,
                "Adj Close": adj_close,
                "Volume": volume
            })

    # Create a DataFrame from the data list
    DF = pd.DataFrame(data)

    # Convert the 'Date' column to datetime format for easy plotting
    DF['Date'] = pd.to_datetime(DF['Date'])

    # Close the driver
    driver.quit() 

    return DF


# Function to build the stock graph
def build_stock_graph(stock_df, plot_columns=["Close"]):
    """
    Function to plot stock prices over time using matplotlib.

    Parameters:
        stock_df (DataFrame): DataFrame containing the stock data.
        plot_columns (list): List of columns to plot (e.g., ["Close", "Open"]).
    """
    # Ensure 'Date' is sorted in ascending order (in case of any sorting issues)
    stock_df = stock_df.sort_values('Date')

    # Set up the plot
    plt.figure(figsize=(12, 6))

    # Loop through the columns to plot
    for column in plot_columns:
        if column in stock_df.columns:
            plt.plot(stock_df['Date'], stock_df[column], label=column)

    # Add labels and title
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.title('Stock Price Over Time')

    # Rotate the date labels for better readability
    plt.xticks(rotation=45)

    # Add grid for better visualization
    plt.grid(True)

    # Add a legend
    plt.legend()

    # Adjust layout to make it more readable
    plt.tight_layout()

    # Display the plot
    plt.show()

# Example usage
stock = "gme"  # You can change this to any stock symbol
df = fetch_stock_data(stock)

# Plotting the graph with the default "Close" price
build_stock_graph(df)

# You can also plot multiple columns like 'Close', 'Open', 'High', and 'Low'
# Example:
# build_stock_graph(df, plot_columns=["Close", "Open", "High", "Low"])
