import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Base URL
base_url = "https://eogdata.mines.edu/nighttime_light/monthly/v10/"

def fetch_directories(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return [
                link.get('href').strip('/')
                for link in soup.find_all('a')
                if link.get('href') and link.get('href').endswith('/')
            ]
        else:
            return []
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

# Step 1: Get all year directories
years = fetch_directories(base_url)
years = sorted(set(year for year in years if year.isdigit()))

# Step 2: Fetch all valid month folders from each year directory
def fetch_months_for_year(year):
    year_url = f"{base_url}{year}/"
    months = fetch_directories(year_url)
    return [m for m in months if m.startswith(year)]

all_months = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_months_for_year, year) for year in years]
    for future in as_completed(futures):
        all_months.extend(future.result())

unique_months = sorted(set(all_months))

# Step 3: Generate the static HTML page
with open("index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Available Nighttime Light Data</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 2em; background: #f9f9f9; }
    h2 { color: #333; }
    ul { list-style: none; padding-left: 0; }
    li { margin: 5px 0; font-size: 16px; }
  </style>
</head>
<body>
  <h2>Available data:</h2>
  <ul>
""")
    for month in unique_months:
        f.write(f'    <li><a href="{base_url}{month}/" target="_blank">{month}</a></li>\n')
    f.write("""  </ul>
</body>
</html>""")
