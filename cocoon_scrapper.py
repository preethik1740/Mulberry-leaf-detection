import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import time

# ----------------------
# PostgreSQL credentials
# ----------------------
DB_NAME = "sericulture"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

# ----------------------
# Website URL
# ----------------------
URL = "https://tnsericulture.tn.gov.in/cocoonmarket"

# ----------------------
# Function to fetch and store data
# ----------------------
def fetch_and_store():
    try:
        # Get page content
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, "html.parser")

        # Find date on website
        # Extract date
        from datetime import datetime

# Extract date
        date_tag = soup.find("h4", {"id": "transdate"})
        if date_tag:
            date_text = date_tag.get_text(strip=True).replace("Date :", "").strip()
            try:
                date_obj = datetime.strptime(date_text, "%d-%m-%Y").date()
            except ValueError:
                print("Date format not recognized:", date_text)
                return
        else:
            print("Date not found on page.")
            return




        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        # Find the price table
        table = soup.find("table", {"class": "table"})
        if table is None:
            print("Price table not found!")
            return

        rows = table.find_all("tr")[1:]  # skip header
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) < 8:
                continue  # skip incomplete rows
            sno, market, hmin, hmax, havg, cmin, cmax, cavg = cols

            # Convert to integers (handle missing values)
            def to_int(x): return int(x) if x.isdigit() else None

            cur.execute("""
                INSERT INTO cocoon_prices 
                (date, market_name, hybrid_min, hybrid_max, hybrid_avg, cross_min, cross_max, cross_avg)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (date, market_name) DO NOTHING;
            """, (date_obj, market, to_int(hmin), to_int(hmax), to_int(havg),
                  to_int(cmin), to_int(cmax), to_int(cavg)))

        conn.commit()
        cur.close()
        conn.close()
        print("Data inserted successfully for", date_obj)

    except Exception as e:
        print("Error:", e)

# ----------------------
# Run daily (every 24h)
# ----------------------
if __name__ == "__main__":
    while True:
        fetch_and_store()
        print("Sleeping for 24 hours...")
        time.sleep(24*60*60)  # sleep for 24 hours
