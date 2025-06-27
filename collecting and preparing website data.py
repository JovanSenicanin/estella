import requests
from bs4 import BeautifulSoup

target_url = "https://sites.google.com/view/estellav2/home"

response = requests.get(target_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ""

    for paragraph in soup.find_all('p'):
        text += paragraph.get_text()

    # Specify encoding='utf-8' to handle all Unicode characters
    with open('website_text.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(text)

    print("Text extracted and saved successfully!")

else:
    print(f"Error: Failed to retrieve website content. Status code: {response.status_code}")
