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

# First iteration to save the sub data
sub_source_list_it_1, sub_code_list_it_1, sub_text_list_it_1 = [], [], []
full_code_it_1, main_source_it_1, main_text_list_it_1 = [], [], []
main_code_list_it_1  = []

# Parse the sub data
sub_code = soup.find_all("ul", class_="ulPopover")
for i, code in enumerate(sub_code, 0):
    for c in code:
        a_link = c.a.get('href') # get href from <a> tag
        a_text = c.text # get the text
        if main_code_list[i] in a_link: # check if main code is in href link (sub code)
            full_code_it_1.append(f"{main_code_list[i]}_{a_link[-7:]}") # get full code (main_sub)
            
            sub_source_list_it_1.append(f"https://www.icd10data.com{a_link}") # get full source of sub code
            sub_code_list_it_1.append(a_link[-7:]) # get sub code from href
            sub_text_list_it_1.append(a_text[8:]) # get text without the code 
            
            main_source_it_1.append(f"https://www.icd10data.com/{main_code_list[i]}") # get main source
            main_code_list_it_1.append(main_code_list[i])
            main_text_list_it_1.append(main_text_list[i])

# Second iteration to save the sub_sub data
sub_sub_source, sub_sub_code_list, sub_sub_text_list = [], [], []
sub_source_list_it_2, sub_code_list_it_2, sub_text_list_it_2 = [], [], []
main_source_it_2, main_code_list_it_2, main_text_list_it_2 = [], [], []
full_code_it_2 = []

# Complete the incomplete sub_text
for i, source in enumerate(sub_source_list_it_1):
    # Define t_it_1he url from sub_source
    url = source

    # Request
    r = requests.get(url, headers=headers)
    text = r.text

    # Bs4
    soup = BeautifulSoup(text, "html5lib")

    if '...' in sub_text_list_it_1[i]:
        # Print the index so we know the program still running
        print(f"index number: {i} > There is '...'")
        
        # Parse he_it_1ading of sub_text based of sub_source
        heading = soup.find_all("h1", class_="pageHeading")
        for h in heading:
            sub_text_list_it_1[i] = h.text[:-9] # edit the sub_text
    else:
        print(f"index number: {i} > There is no '...'")

    # Parse sub_sub_text based inside ul
    list_sub_sub_text = []
    sub_sub_text = soup.find_all("ul", class_="i51")
    for text in sub_sub_text:
        text = text.text
        text = text.strip().replace("\n", "|")
        list_sub_sub_text.append(text)

    # Remove trailing spaces from sub_sub_text
    for sub_sub_text in list_sub_sub_text:
        sub_text = sub_sub_text.split('|')
        for text in sub_text:
            no_spaces = text.strip()
            # Append non-empty text only
            if no_spaces:
                full_code_it_2.append(f"{full_code_it_1[i]}_{no_spaces[:3]}")
                
                main_source_it_2.append(main_source_it_1[i])
                main_code_list_it_2.append(main_code_list_it_1[i])
                main_text_list_it_2.append(main_text_list_it_1[i])

                sub_source_list_it_2.append(sub_source_list_it_1[i])
                sub_code_list_it_2.append(sub_code_list_it_1[i])
                sub_text_list_it_2.append(sub_text_list_it_1[i])
                
                sub_sub_source.append(f"{sub_source_list_it_1[i]}/{no_spaces[:3]}")
                sub_sub_code_list.append(no_spaces[:3])
                sub_sub_text_list.append(no_spaces[5:])
                
                print(f"Row {i} updated.")

# Convert parsed data into dataframe
df = {
    "full_code": full_code_it_2,
    "main_source": main_source_it_2,
    "main_code": main_code_list_it_2,
    "main_text": main_text_list_it_2,
    "sub_source": sub_source_list_it_2,
    "sub_code": sub_code_list_it_2,
    "sub_text": sub_text_list_it_2,
    "sub_sub_source": sub_sub_source,
    "sub_sub_code": sub_sub_code_list,
    "sub_sub_text": sub_sub_text_list,
}
df = pd.DataFrame.from_dict(df)

# Save the parsed data to a csv file
filename = "parsed_data/parsed_icd_10_cm_data.csv"
df.to_csv(filename, index=False, sep="|")
print(f"Saved as {filename}")
