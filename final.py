import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def get_third_item_text(soup):
    outer_div = soup.find('div', class_='hidden-xs')

    if outer_div:
        year_verson_div = outer_div.find('div', class_='year-verson-type')

        if year_verson_div:
            ul_tag = year_verson_div.find('ul')

            if ul_tag:
                li_tags = ul_tag.find_all('li')
                if len(li_tags) >= 3:
                    third_li = li_tags[2]
                    p_tag = third_li.find('p')

                    if p_tag:
                        text = p_tag.get_text(strip=True)
                        return text
    return 'Category not found'

def process_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    outer_divs = soup.find_all('div', class_='tab-con-detail-tab')

    description = ''
    for outer_div in outer_divs:
        nested_div = outer_div.find('p', class_='poppins-regular')

        if len(nested_div) == 1:
            description = nested_div.get_text(separator='\n', strip=True)
            break

    title_tag = soup.find('title')
    product_name = title_tag.text.split('|')[0].strip() if title_tag else 'Product name not found'
    script_tag = soup.find('script', {'type': 'application/ld+json'})
    if script_tag:
        json_data = script_tag.string.strip()
        data = json.loads(json_data)
        brand_name = data['brand']['name'] if 'brand' in data else 'Brand name not found'
        price = data['offers']['price'] if 'offers' in data and 'price' in data['offers'] else 'Price not found'
    else:
        brand_name = 'Brand name not found'
        price = 'Price not found'

    catagory = get_third_item_text(soup)
    image_meta = soup.find('meta', {'property': 'og:image'})
    image_url = image_meta['content'] if image_meta else 'Image URL not found'

    return {
        'URL': url,
        'Product Name': product_name,
        'Brand Name': brand_name,
        'Price': price,
        'Category': catagory,
        'Image URL': image_url,
        'Description': description
    }


with open('url_list.csv', 'r') as file:
    urls = [line.strip() for line in file.readlines()]


results = [process_url(url) for url in urls]


df = pd.DataFrame(results)
df.to_csv('data.csv', index=False)
print("Sir Your work is Done!")
