from operator import le
import requests
from bs4 import BeautifulSoup
import re
import psycopg2


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


def write_info_to_file(file_name, raw_data_list):
    with open(file_name, 'a') as file:
        for item in raw_data_list:
           
            file.write(str(item.description))
            file.write("\n")

            file.write(str(item.link))
            file.write("\n")

            file.write(str(item.price))
            file.write("\n")
            file.write("\n")
            file.write("\n")


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
    write_info_to_file(text_file_name, products_collected)

print(f"The data from the site was saved on a text file: {text_file_name}")

conn = psycopg2.connect(database="test1", user="postgres", password="postgres", host="192.168.1.7", port="5432")
cur = conn.cursor()
cur.execute("CREATE TABLE test_table(id serial PRIMARY KEY, price float, description CHAR(500));")
print("Table Created....")
cur.execute("INSERT INTO test_table (id, sname, roll_num) \
      VALUES (1, 150.48, 'Headphones')");

cur.execute("INSERT INTO test_table (id, sname, roll_num) \
      VALUES (2, 55.99,'Mouse')");

cur.execute("INSERT INTO test_table (id, sname, roll_num) \
      VALUES (3, 480.50, 'Monitor')");

cur.execute("INSERT INTO test_table (id, sname, roll_num) \
      VALUES (4, 2999.99, 'Laptop')");

conn.commit()
print("Records created successfully");
conn.close()