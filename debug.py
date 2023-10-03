# import requests
# import json

# headers = {
#     "authorization": "Bearer ya29.a0AfB_byCcfymzlNw5szhbc9emn95d8XEarGiYk5HjzBuELYpjTRTn1-1F14-FDESTxHM8z64NAHmE8t6rhgmMOrGdvbNkCjFdh2ozzaIDx3f4I570h6m1ONw6wCAqsAT6GMKdig82EsLsRgAPOdNAyCndV3dxn-xeLhiFaCgYKAXsSARESFQGOcNnC0z5DsWEWn2cjdh7RKV4Ecw0171",
# }

# params = {
#     "name": 'data_10.db',
#     "parents": ['1J_gWE3b8cFGH41E_zUM8al1GKnDRcbrd']
# }

# files = {
#     'data': ('metadata', json.dumps(params), 'application/json;charset=UTF-8'),
#     'file': ('data_10.db', open('/home/puppeteer/data_10.db', 'rb'), 'application/db')
# }

# res = requests.post(
#     'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',
#     headers=headers,
#     files=files
# )
# print(res)
# print(res.text)


import psutil

def get_chromium_processes():
    chromium_processes = []
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'chromium' in process.info['name'].lower() or 'chrome' in process.info['name'].lower():
                chromium_processes.append(process.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return chromium_processes

def print_chromium_processes():
    k=0
    chromium_processes = get_chromium_processes()

    if chromium_processes:
        # print(f"Number of Chromium processes: {len(chromium_processes)}")
        print("\nDetails of Chromium processes:")
        for process in chromium_processes:
            # if '--user-data-dir=/home/puppeteer/USER_DIR' in ' '.join(process['cmdline']):
            #     continue
            # if 'chrome_crashpad_handler' in process['name']:
            #     continue
            print(f"PID: {process['pid']}")
            print(f"Name: {process['name']}")
            print(f"Command Line: {' '.join(process['cmdline'])}\n")
            k+=1
    else:
        print("No Chromium processes found.")
    print(k,'processes')
if __name__ == "__main__":
    print_chromium_processes()
