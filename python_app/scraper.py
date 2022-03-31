from operator import le
import requests
from bs4 import BeautifulSoup
import re
import psycopg2
import sys


class ProductInfo:
    def __init__(self):
        self.price = 0.0
        self.link = ""
        self.description = ""

    def encode_product_info_uft8(self):

        encoded_product = ProductInfo()

        encoded_product.description = self.description
        encoded_product.link = self.link
        encoded_product.price = str(self.price)
        return encoded_product


def leave_only_price(text):
    regexNum = r"\d+"

    matchesNum = re.findall(regexNum, text, re.MULTILINE)
    lev=matchesNum[0]
    stotinki=matchesNum[1]
    price=float(lev)+float(stotinki)/100
    return price

def get_link(text):
    regexLink = r"href=[\'\"]?([^\'\" >]+)"
    matches = re.search(regexLink, text, re.MULTILINE)
    #print(text)
    if matches:
        return matches.group(1)
    else:
        return "Link not found"

def get_items_form_emag(link):
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.select('.card-v2')

    all_products = []

    for product in items:

        try:
            current_product = ProductInfo()

            info = product.select('.card-v2-content')
            # Get price for current product
            current_product.price = leave_only_price(product.select('.product-new-price')[0].getText())

            # Gets the link to the page of the current product
            current_product.link = get_link(str(product.select('.pad-hrz-xs')[0]))

            # Gets the basic card description of the current product
            current_product.description = product.select('.pad-hrz-xs')[0].getText().replace("\n","")

            # Adds the current product to the list of all products as a dict
            all_products.append(current_product)
        except IndexError:
            # print("End of page!")
            break

    return all_products


def write_info_to_db(file_name, raw_data_list):
    db_user = str(sys.argv[1])
    db_pass = str(sys.argv[2])
    db_host = str(sys.argv[3])
    db_port = str(sys.argv[4])
    db_name = str(sys.argv[5])
    db_table_name = str(sys.argv[6])
    conn = psycopg2.connect(database="postgres", user=f"{db_user}", password=f"{db_pass}", host=f"{db_host}", port=f"{db_port}")
    conn.autocommit=True
    cur = conn.cursor()

    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {db_name}")
        conn.commit()
    conn.close()

    conn = psycopg2.connect(database=f"{db_name}", user=f"{db_user}", password=f"{db_pass}", host=f"{db_host}", port=f"{db_port}")
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {db_table_name}(id SERIAL PRIMARY KEY, price FLOAT, description CHAR(500), url CHAR(500));")
    print("Table Created....")

    for item in raw_data_list:
        cur.execute(f"INSERT INTO slushalki_prices (price, description, url) \
        VALUES ({float(item.price)}, '{str(item.description)}', '{str(item.link)}')");

    conn.commit()
    print("Records created successfully");
    conn.close()


def get_next_link(link, page_num=0):
    if page_num == 0:
        link = link + r"/c"
    else:
        link = link + r"/p" + str(page_num) + r"/c"
    return link


def input_positive_int():
    """ Returns only a positive integer. Returns only if the user inputs a positive integer."""
    while True:
        try:
            user_number = int(input('Pages: '))

            if user_number <= 0:
                raise ValueError("The given number must be a positive integer")
        except ValueError as err:
            print(f"Please enter a valid whole number larger than 0! ({err})")
            pass
        else:
            break

    return user_number


my_link = r"https://www.emag.bg/slushalki-kompiutyr"
text_file_name = "testNew.txt"
number_of_pages = 0

for number in range(number_of_pages + 1):
    products_collected = get_items_form_emag(get_next_link(my_link, number))
    write_info_to_db(text_file_name, products_collected)

print(f"The data from the site was saved on a the postgresql")
