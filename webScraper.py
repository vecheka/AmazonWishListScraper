import urllib.request
import requests
from bs4 import BeautifulSoup
import csv
import time
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

FROM_EMAIL = "some@email.com"
TO_EMAIL = "some@email.com"
PASSWORD = "****"
UNKNOWN = "Unknown"

headers = {
    "User-Agent": "Web crawler. Contact me at cvecheka07@gmail.com"
}
## Http address of the targeted url
LINK_HEADER = "https://www.amazon.com"
## File name to store the data
FILE_NAME = "items_info.csv"



## Fetch data from the targeted url
def fetchData():
    try:
        # targeted url
##        wiki = "https://www.amazon.com/hz/wishlist/ls/10DP6ESCAUH9Q/ref=nav_wishlist_lists_2?_encoding=UTF8&type=wishlist"
        wiki = "https://www.amazon.com/hz/wishlist/ls/3NZFUWEQXRL84/?ref_=lol_ov_le#"
        # get permission from the page
        page = requests.get(wiki, headers = headers, timeout = 5)

        # page's contents
        soup = BeautifulSoup(page.text, "html.parser")

        # get items' prices
        item_prices = []
        for prices in soup.find_all("span", "a-price-whole"):
            item_prices.append(prices.text.strip().replace(".", "").replace(",", ""))

        # get contents from specific class or id
        item_contents = soup.select(".a-size-base > a")
        item_info = [["Name", "Price($)", "Link"]]
        index = 0
        if item_contents:
            for item in item_contents:
                content = item.contents
                item_name = content[0].split(",")[0]
                if (index >= len(item_prices)) :
                     item_info.append([item_name, UNKNOWN, LINK_HEADER + item["href"]])
                else:
                     item_info.append([item_name, item_prices[index], LINK_HEADER + item["href"]])
               
                index += 1
            return item_info
        else:
            print("Failed to fetch data.")
    except requests.ConnectionError as theE:
        print("OPPS! Connection Error. Make sure you are connected to the Internet.\n")
        print(str(theE))
    except requests.Timeout as theE:
        print("OPPS! Timeout Error")
        print(str(theE))
    except requests.RequestException as theE:
        print("OPPS! General Error")
        print(str(theE))
    except KeyboardInterrupt:
        print("Program was closed by someone")
        

## write items's information to .csv file
def writeToFile(item_info):

    with open(FILE_NAME, "w") as f:
        writer = csv.writer(f)

        for item in item_info:
            writer.writerow(item)

## read items' information from .csv file
def readFromFile():
    item_info = []
    with open(FILE_NAME) as File:
        reader = csv.reader(File, delimiter = ",", quotechar = ",",
                            quoting = csv.QUOTE_MINIMAL)
        for row in reader:
           if (row):
               item_info.append(row)

    return item_info


## compare if the items' prices have changed, and notify the owner through email
## if there is a change
def comparePrice():
    originalItems_info = readFromFile()
    updatedItems_info = fetchData()

    hasDropped = False
    for i in range(1, len(originalItems_info)):
        price1 = originalItems_info[i][1]
        price2 = updatedItems_info[i][1]
        if (price1 != UNKNOWN and price2 != UNKNOWN):
            price1 = int(price1)
            price2 = int(price2)
            if (price1 > price2):
                notify(originalItems_info[i], updatedItems_info[i])
                hasDropped = True
        else:
            print("Unknown Price. Please visit item's link to find out more. \nLink: " + originalItems_info[i][2])


    if hasDropped:
        writeToFile(updatedItems_info)

    
## notify the owner via email if any items' price in the wish list has changed
def notify(original_item, updated_item):
    try:
        s = smtplib.SMTP(host = "smtp.gmail.com", port = 587)
        s.starttls()
        s.login(FROM_EMAIL, PASSWORD)

        msg = MIMEMultipart() # create a message
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg["Subject"] = "Item's Price Goes Down!"

        message = original_item[0] + "'s price has changed from " + "$" + original_item[1] + " to $" + updated_item[1] + "\n" + original_item[2]

        msg.attach(MIMEText(message, 'plain'))

        s.send_message(msg)
        del msg

        s.quit()
    except:
        print("Something went wrong...")

## main class
def main():
    
    
    item_info = fetchData()

    if (item_info):
        writeToFile(item_info)
    while (True):
        comparePrice()
        print("Web Crawler's going to sleep for a day")
        time.sleep(3600 * 24)
        print("Web Crawler's awake!")

    print("Done!")

main()

