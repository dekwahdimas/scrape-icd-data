import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define the URL to scrape
url = "https://www.icd10data.com/ICD10CM/Codes"

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

# Request
r = requests.get(url, headers=headers)
text = r.text

# Bs4
soup = BeautifulSoup(text, "html5lib")

# Parse the main text of each code
main_text_list = []
main_text = soup.find_all("h2", class_="codeDescriptionPopover")
for text in main_text:
    main_text_list.append(text.text)

# Parse the main code of each code
main_code_list = []
main_code = soup.find_all("span", class_="identifier")
for code in main_code:
    main_code_list.append(code.text)

# Parse the sub code of each main code
# Also, recreate the main part so it will be on the same row as the sub part
sub_source, sub_code_list, sub_text_list = [], [], []
full_code, new_main_code_list, new_main_text_list = [], [], []
i = -1 # I'm sorry if this looks stupid, but I am honestly glad it worked
sub_code = soup.find_all("ul", class_="ulPopover")
for code in sub_code:
    i += 1 # +1 after first iteration
    for c in code:
        a_link = c.a.get('href') # get href from <a> tag
        a_text = c.text # get the text
        if main_code_list[i] in a_link: # check if main code is in href link (sub code)
            sub_source.append(f"https://www.icd10data.com{a_link}") # get full source of sub code
            sub_code_list.append(a_link[-7:]) # get sub code from href
            sub_text_list.append(a_text[8:]) # get text without the code 
            full_code.append(f"{main_code_list[i]}_{a_link[-7:]}") # get full code (main_sub)
            new_main_code_list.append(main_code_list[i])
            new_main_text_list.append(main_text_list[i])
        else:
            sub_source.append("no_sub_source")
            sub_code_list.append("no_sub_code")
            sub_text_list.append("no_sub_text")
            full_code.append("no_full_code")
            new_main_code_list.append("no_main_code")
            new_main_text_list.append("no_main_text")

# Convert parsed data into dataframe and save it to a csv file
df = {
    "full_code": full_code,
    "main_code": new_main_code_list,
    "main_text": new_main_text_list,
    "sub_source": sub_source,
    "sub_code": sub_code_list,
    "sub_text": sub_text_list,
}
df = pd.DataFrame.from_dict(df)
df.to_csv("parsed_icd_10_cm_data.csv", index=False, sep="|")
