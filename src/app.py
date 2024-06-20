import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt

# Step 1: Fetch HTML, Parse Data

# Step 2: Download HTML with a User-Agent Header
url = "https://ycharts.com/companies/TSLA/revenues"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
response.raise_for_status()
html_content = response.text

# Continue with the rest of your script
soup = BeautifulSoup(html_content, 'html.parser')
tables = soup.find_all('table')

# Assuming the first table contains the data we need
table = tables[0]

# Extract table headers
headers = [header.text.strip() for header in table.find_all('th')]

# Extract table rows
rows = table.find_all('tr')
data = []
for row in rows[1:]:
    cells = row.find_all('td')
    cells = [cell.text.strip() for cell in cells]
    data.append(cells)

# Create DataFrame
df = pd.DataFrame(data, columns=headers)

print(df)

# Step 3: Process DataFrame

# Clean up 'Value' column: remove $, commas, and 'B', then convert to numeric
df['Value'] = df['Value'].replace({'\$': '', ',': '', 'B': ''}, regex=True).astype(float)

# Step 4: Store Data in SQLite

# Create an SQLite database and connect
engine = create_engine('sqlite:///tesla_revenue.db')
connection = engine.connect()

# Drop the table if it already exists using SQLAlchemy text
drop_statement = text("DROP TABLE IF EXISTS Value")
connection.execute(drop_statement)

# Store the DataFrame in SQLite using the engine object, not a string
df.to_sql('Value', con=engine, if_exists='replace', index=False)

# Close the connection
connection.close()

# Step 5: Visualize Data

# Convert the 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Sort the DataFrame by date
df = df.sort_values(by='Date')

# Bar Plot of Annual Revenue
df['Year'] = df['Date'].dt.year
annual_revenue = df.groupby('Year')['Value'].sum()

# Plotting the data (optional, if matplotlib is properly installed)
plt.bar(annual_revenue.index, annual_revenue.values)
plt.xlabel('Year')
plt.ylabel('Annual Revenue')
plt.title('Tesla Annual Revenue')
plt.xticks(annual_revenue.index)
plt.grid(True)
plt.show()
