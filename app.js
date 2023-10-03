const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const fs = require("fs");
const fsPromises = require('fs').promises;

const winston = require('winston');
const { combine, timestamp, label, printf } = winston.format;
const { File } = require('winston').transports;

const myFormat = printf(({ level, message, label, timestamp }) => {
  return `${timestamp} [${label}] ${level}: ${message}`;
});

const logger = winston.createLogger({
  level: 'info',
  format: combine(
    label({ label: 'Testing' }),
    timestamp(),
    myFormat
  ),
  transports: [
    new File({ filename: '/home/puppeteer/DEBUG LOGs/node/error.log', level: 'error' }),
    new File({ filename: '/home/puppeteer/DEBUG LOGs/node/info.log', level: 'info' }),
    new File({ filename: '/home/puppeteer/DEBUG LOGs/node/combined.log' })
  ]
});

puppeteer.use(StealthPlugin());

const [,, productURL, req_id] = process.argv;

async function scrapeProductData(url) {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/chromium-browser",
    headless: "new",
    // set user dir /home/puppeteer/USER_DIR/{req_id}
    args: [
      "--user-data-dir=/home/puppeteer/USER_DIR/" + req_id,
      "--lang=en-IN",
      "--no-default-browser-check",
      "--no-first-run",
      "--no-sandbox",
      "--test-type",
      "--window-size=1920,1080",
      "--start-maximized",
      "--no-sandbox",
      "--log-level=0",
      "--flag-switches-begin",
      "--flag-switches-end",
      "--disable-nacl",
      '--disable-breakpad',
      `--load-extension=/home/puppeteer/extension`,
      '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      // disable images
      '--blink-settings=imagesEnabled=false',
      // disable chrome crash reporting
      '--disable-component-update',
      '--disable-default-apps',
      '--disable-domain-reliability',
      '--disable-gpu',
      '--disable-hang-monitor',
      '--disable-infobars',
      '--disable-notifications',
      '--disable-offer-store-unmasked-wallet-cards',
      '--disable-offer-upload-credit-cards',
      '--disable-popup-blocking',
      '--disable-print-preview',
      '--disable-prompt-on-repost',
      '--disable-setuid-sandbox',
      '--disable-speech-api',
      '--disable-sync',
      '--hide-scrollbars',
      
      
    ],
  });

  const page = await browser.newPage();

  try {
    try {
      // timeout 1 minute
      await page.goto(url, {timeout: 60000 });
     
      logger.info(`${req_id} | Successfully navigated to ${url}\n`);
    } catch (e) {
      logger.error(`${req_id} | Failed to navigate to ${url}\n`);
      
    }
    

    if (page.url().includes("buyer/login?")) {
      logger.error(`${req_id} | Login page detected\n`);
      return "Login page detected";
    }

    logger.info(`${req_id} | Current URL: ${page.url()}\n`);

    const product_name_text = await waitForElementWithTimeout(
      page,
      "div._44qnta span",
      60000
    );

    if (!product_name_text) {
      logger.error(`${req_id} | Failed to get product name\n`);
      await page.screenshot({ path: `/home/puppeteer/screenshot/${req_id}_product_name.png`, fullPage: true });
      // throw new Error("Failed to get product name");
      throw new Error("Failed to get product name!");
   

    }

    let cat_id_text, cat_id_, itemid = null;
    try {
      cat_id_text = await page.evaluate(() => {
        const anchors = document.querySelector("a.W0LQye")?.href;
        return anchors;
      });
    } catch (e) {
      logger.error(`${req_id} | Failed to get category id\n`);
    }
    
    if (cat_id_text !== null) {
      cat_id_ = extractCategoryId(cat_id_text);
      itemid = extractItemId(cat_id_text);
    }
    const price_text = await waitForElementWithTimeout(page, "div.pqTWkA", 10000);
    let sold_text = await waitForElementWithTimeout(page, "div.P3CdcB", 10000);

    if (!sold_text) {
      sold_text = await page.evaluate(() => {
        const anchors = document.querySelector("div.e9sAa2")?.innerText;
        return anchors;
      });
    }

    const sold_int = parseInt(sold_text);

    const evaluate_text = await waitForElementWithTimeout(
      page,
      "._1k47d8",
      5000
    );
    const evaluate_int = parseInt(evaluate_text);

    const rating_text = await waitForElementWithTimeout(
      page,
      "div._1k47d8._046PXf",
      5000
    );
    const rating_float = parseFloat(rating_text);

    const category_text = await waitForElementWithTimeout(
      page,
      ".flex.items-center.RnKf-X",
      5000
    );

    if (category_text) {
      const find_ids = category_text.match(/-i.[0-9]+.[0-9]+/g);

      if (find_ids && find_ids.length > 0) {
        const find_ids_ = find_ids[0].replace("-i.", "").split(".");
        let shopid = null;

        try {
          shopid = parseInt(find_ids_[0]);
        } catch (e) {
          logger.error(`${req_id} | Failed to parse shopid\n`);
        }

        if (shopid !== null) {
          // Rest of your code here
        } else {
          logger.error(`${req_id} | Failed to parse shopid\n`);
        }
      } else {
        logger.error(`${req_id} | No matching IDs found\n`);
      }
    } else {
      logger.error(`${req_id} | Category text not found within the specified timeout\n`);
    }

    const data = {
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

    return data;
  } catch (error) {
    logger.error(`${req_id} | Error scraping data from URL ${url}: ${error.message}\n`);
    return null;
  } finally {
    await browser.close();
   
  }
}

async function waitForElementWithTimeout(page, selector, timeout) {
  try {
    await page.waitForSelector(selector, { timeout });
    const element = await page.$(selector);

    if (element) {
      return await page.evaluate((el) => el.textContent, element);
    } else {
      logger.error(`${req_id} | Element with selector ${selector} not found\n`);
      return null;
    }
  } catch (error) {
    logger.error(`${req_id} | Error waiting for element with selector ${selector}: ${error.message}\n`);
    return null;
  }
}



function extractCategoryId(url) {
  const categoryIdMatch = url.match(/categoryId=([0-9]+)/);
  return categoryIdMatch ? parseInt(categoryIdMatch[1]) : null;
}

function extractItemId(url) {
  const itemIdMatch = url.match(/itemId=([0-9]+)/);
  return itemIdMatch ? parseInt(itemIdMatch[1]) : null;
}


// process.on('unhandledRejection', (reason, promise) => {
//   console.error('Unhandled Rejection at:', promise, 'reason:', reason);
//   // remove user dir
//   removeUserDir();
//   process.exit(0);
// });


// function to check and remove user dir
async function removeUserDir() {
  const dir = `/home/puppeteer/USER_DIR/${req_id}`;
  try {
    if (await fsPromises.access(dir).then(() => true).catch(() => false)) {
      await fsPromises.rm(dir, { recursive: true });
      logger.info(`${req_id} | User dir removed\n`);
    } else {
      logger.info(`${req_id} | User dir not found\n`);
    }
  } catch (err) {
    logger.error(`${req_id} | Failed to remove user dir\n`);
  }
}


logger.info(`${req_id} | Scraping data from URL ${productURL}...\n`);



scrapeProductData(productURL)
  .then((data) => {
    logger.info(`${req_id} | Scraping completed | data: ${JSON.stringify(data)}\n`);
    if (data) {
      try{
      if (data === "Login page detected") {
        logger.error(`${req_id} | Login page detected\n`);
        console.log(`Login page detected |**| req_id: ${req_id} |**|`);
        return;
      }
    }catch(e){
    }
      logger.info(`${req_id} | Successfully scraped data.\n`);
      logger.info(`${req_id} | ${JSON.stringify(data)}\n`);
      fs.writeFile(`/home/puppeteer/output/${req_id}.json`, JSON.stringify(data), function (err) {
        if (err) throw err;
        logger.info(`${req_id} | Saved data as JSON.\n`);
        let path = `/home/puppeteer/output/${req_id}.json`;
        console.log(`Saved data as JSON |**| path: ${path} |**|`);
      });
    } else {
      logger.error(`${req_id} | Failed to scrape data.\n`);
      console.log(`Failed to scrape data |**| req_id: ${req_id} |**|`);
    }
  })
  .catch((error) => {
    logger.error(`${req_id} | Failed to scrape data.\n`);
    console.log(`Failed to scrape data |**| req_id: ${req_id} |**|`);
  })
  .finally(() => {
    // remove user dir
    removeUserDir();
    // process.exit(0);
  });
