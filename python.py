import subprocess
import sqlite3
import json
import logging
import time
import os
from concurrent.futures import ThreadPoolExecutor
import re
# import uuid
import uuid

import random

# config logging
logging.basicConfig(
    filename='/home/puppeteer/DEBUG LOGs/python/log_10.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
    
)

control =[False]*15
arr = []
with open('result.txt', 'r') as f:
    for line in f:
        arr.append(line.strip())

arr+=arr
        
'''
if table not exist create table
data    {
      "req_id": req_id,
      "Product URL": url,
      "Name": product_name_text,
      "Category_id": cat_id_,
      "Item_id": itemid,
      "Category": category_text,
      "Price": price_text,
      "Rating": rating_float,
      "Evaluate": evaluate_int,
      "Sold": sold_int,
    };
'''
# with it add time in db 
conn = sqlite3.connect('data_10.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS data
                (req_id text, url text, product_name_text text, cat_id_ text, itemid text, category_text text, price_text text, rating_float text, evaluate_int text, sold_int text , time,error, retry_count, login_count)''')

def scrape_data(ip_url,retry_count=0,login_count=0,req_id=None):
    global control
    proxy()
    if not req_id:
        req_id = str(uuid.uuid4())
    start_time = time.time()

    logging.info(f"start scrape data {ip_url} | index: {arr.index(ip_url)+1}")

    try:
        terminal = subprocess.Popen(['node', 'app.js', f"{ip_url}", f"{req_id}"], stdout=subprocess.PIPE)
        output = terminal.stdout.read()
        output = output.decode("utf-8")

        if "Saved data as JSON |**| path:" in output:
            path = output.split("|**|")[1].strip().split('|**|')[0].strip("path:").strip()

            with open(path, 'r') as f:
                data = json.load(f)
                url = data['Product URL']
                product_name_text = data['Name']
                cat_id_ = data['Category_id']
                itemid = data['Item_id']
                category_text = data['Category']
                price_text = data['Price']
                rating_float = data['Rating']
                evaluate_int = data['Evaluate']
                sold_int = data['Sold']
                end_time = time.time() - start_time

                c.execute(
                    "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?)",
                    (
                        req_id, 
                        url,
                        product_name_text,
                        cat_id_,
                        itemid,
                        category_text,
                        price_text,
                        rating_float,
                        evaluate_int,
                        sold_int,
                        end_time,
                        None,
                        retry_count,
                        login_count,
                    )
                )

                conn.commit()
                os.remove(path)
        
        elif 'Login page detected' in output:
            return scrape_data(ip_url, retry_count, login_count+1,req_id)
        elif 'Failed to scrape data |**| req_id:' in output:
            logging.error("Failed to scrape data |**| req_id: {}".format(req_id))
            end_time = time.time() - start_time
            if retry_count < 5:
                return scrape_data(ip_url, retry_count+1, login_count,req_id)
            c.execute(
                "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?)",
                (
                    req_id, 
                    ip_url,
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    end_time,
                    output,
                    retry_count,
                    login_count,
                )
            )
            conn.commit()
        else:
            logging.error("Failed to scrape data |**| req_id: {}".format(req_id))
            logging.warning(output)
            end_time = time.time() - start_time
            c.execute(
                "INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?)",
                (
                    req_id ,
                   ip_url,
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    end_time,
                    output,
                    retry_count,
                    login_count,
                )
            )
            conn.commit()

        logging.info(f"{'*' * 50} \n\n")

    except Exception as e:
        logging.error(f"somthing went wrong index: {arr.index(i)+1}| error: {e}")
        logging.warning(output)
   
    control[control.index(True)] = False
   


        

# 30738


def proxy():
    # /home/puppeteer/extension/background.js
    port =  [
            10000,
            10001,
            10002,
            10003,
            10004,
            10005,
            10006,
            10007,
            10008,
            10009,
            10010,
            10011,
            10012,
            10013,
            10014,
            10015,
            10016,
            10017,
            10018,
            10019,
            10020,
            10021,
            10022,
            10023,
            10024,
            10000,
            10001,
            10002,
            10003,
            10004,
            10005,
            10006,
            10007,
            10008,
            10009,
            10010,
            10011,
            10012,
            10013,
            10014,
            10015,
            10016,
            10017,
            10018,
            10019,
            10020,
            10021,
            10022,
            10023,
            10024,
        ]
    
    port = random.choice(port)
    js_file ='''
    
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "private.residential.proxyrack.net",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "relu;country=MY,PH,TH,ID-refreshMinutes-3",
                    password: "7d35d7-123852-7e371e-8a2bf4-8e8ad8"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );

        
    '''%(port)
   
        
    with open('/home/puppeteer/extension/background.js', 'w') as f:
        f.write(js_file)


def main():
    global control
    with ThreadPoolExecutor(max_workers=15) as executor:
        try:
            for i in arr:
                while True:
                    if False in control:
                        executor.submit(scrape_data, i)
                        control[control.index(False)] = True
                        break
                    else:
                        time.sleep(5)
                        continue
        except Exception as e:
            logging.error(f"error in main function {e}")
            pass
    
    
    logging.info("close db") 
    conn.close()
    
    
if __name__ == "__main__":
    main()
    #   1722