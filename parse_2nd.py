import requests
from bs4 import BeautifulSoup
import pandas as pd

# Get the headers using burp suite
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=0, i",
    "Connection": "keep-alive"
}

# Check on the saved csv
df = pd.read_csv("parsed_data/parsed_1st_icd_10_cm_data.csv", delimiter="|")

# Complete the incomplete sub_text
for i, source in df.iterrows():
    i += 1
    if '...' in source["sub_text"]:
        # Print the index so we know the program still running
        print(f"index number: {i} > There is '...'")
        # Define the url from sub_source
        url = source["sub_source"]

        # Request
        r = requests.get(url, headers=headers)
        text = r.text

        # Bs4
        soup = BeautifulSoup(text, "html5lib")

        # Parse heading of sub_text based of sub_source
        heading = soup.find_all("h1", class_="pageHeading")
        for h in heading:
            source["sub_text"] = h.text[:-9] # edit the sub_text
            print("DataFrame updated.")
        
    else:
        print(f"index number: {i} > There is no '...'")

# Save the parsed data to a csv file
filename = "parsed_data/parsed_2nd_icd_10_cm_data.csv"
df.to_csv(filename, index=False, sep="|")
print(f"Saved as {filename}")

'''
The csv file output is a complete text for every data.
But, we still need the last code and text to complete the data. 
Use third_parse.py to complete it.
'''
