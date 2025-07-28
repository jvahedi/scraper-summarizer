import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tqdm import tqdm

from GPT_RAND import respond
import glob
import os

# List of site-specific selectors for extracting article content
site_selectors = [
    ('proquest.com', (By.CSS_SELECTOR, "div.display_record_text_copy")),
    ('justice.gov', (By.CSS_SELECTOR, "div.field--name-body")),
    ('cnn.com', (By.CSS_SELECTOR, "div.article__content, div.l-container")),
    ('nytimes.com', (By.CSS_SELECTOR, "section[name='articleBody'], section[data-testid='article-body']")),
    ('abcnews.go.com', (By.CSS_SELECTOR, "div.Article__Content, div.article-copy")),
    ('cbsnews.com', (By.CSS_SELECTOR, "div.article-content, div.content__body")),
    ('washingtonpost.com', (By.CSS_SELECTOR, "article div[data-qa='article-body'], div.article-body")),
    ('nbcnews.com', (By.CSS_SELECTOR, "div.article-body__content, div.article-body")),
    ('foxnews.com', (By.CSS_SELECTOR, "div.article-body, div.article-content")),
    ('apnews.com', (By.CSS_SELECTOR, "div.Article, div.ArticlePage-articleBody")),
    ('usatoday.com', (By.CSS_SELECTOR, "div.gnt_ar_b, div.article-body")),
    ('reuters.com', (By.CSS_SELECTOR, "div.article-body__content, div.StandardArticleBody_body")),
    ('theguardian.com', (By.CSS_SELECTOR, "div.article-body-commercial-selector, div.content__article-body")),
    ('latimes.com', (By.CSS_SELECTOR, "div.article-body, div[data-testid='article-body']")),
    ('npr.org', (By.CSS_SELECTOR, "div.storytext, div.article-body")),
    ('wikipedia.org', (By.CSS_SELECTOR, "div.mw-parser-output")),
    ('dailymail.co.uk', (By.CSS_SELECTOR, "div.article-text, div[itemprop='articleBody']")),
    ('nydailynews.com', (By.CSS_SELECTOR, "div.article-content, div.story-body")),
    ('startribune.com', (By.CSS_SELECTOR, "div.article__body, div.c-article-body")),
    # Add more as needed...
]

# List of default selectors to try if no site-specific selector matches
default_selectors = [
    (By.TAG_NAME, "article"),
    (By.CSS_SELECTOR, "div[itemprop='articleBody']"),
    (By.CSS_SELECTOR, "section[name='articleBody']"),
    (By.CSS_SELECTOR, "div.article-body"),
    (By.CSS_SELECTOR, "div.article-content"),
    (By.CSS_SELECTOR, "div.story-body"),
    (By.CSS_SELECTOR, "div.main-content"),
    (By.CSS_SELECTOR, "div#story"),
    (By.CSS_SELECTOR, "div.entry-content"),
    (By.CSS_SELECTOR, "div.post-content"),
]

def scrape_article(driver, url, debug=False):
    """
    Scrape the main article text from a given URL using Selenium.

    Args:
        driver: Selenium WebDriver instance.
        url (str): The URL of the article to scrape.
        debug (bool): If True, print debug information.

    Returns:
        str or None: The extracted article text, or None if not found.
    """
    article_text = []
    wait = 0
    found = False
    if debug:
        print("="*80)
        print(f"[DEBUG] Starting scrape_article for URL: {url}")
    try:
        if debug: print(f"[DEBUG] Setting page load timeout to 15 seconds.")
        try:
            driver.set_page_load_timeout(15)
            if debug: print(f"[DEBUG] Attempting driver.get({url})")
            driver.get(url)
            if debug: print(f"[DEBUG] Page loaded successfully for {url}")
        except Exception as e:
            #print(f"[ERROR] Page load failed for {url}: {e}")
            return None

        # Site-specific selectors
        target = None
        for domain, selector in site_selectors:
            if domain in url:
                if debug: print(f"[DEBUG] Matched domain '{domain}' in URL. Using site-specific selector: {selector}")
                target = selector
                break
        if not target and debug:
            print(f"[DEBUG] No site-specific selector matched for {url}")

        if target:
            try:
                if debug: print(f"[DEBUG] Waiting up to 8s for site-specific selector: {target}")
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(target)
                )
                wait += 7
                if debug: print(f"[DEBUG] Site-specific selector found. Extracting container and paragraphs.")
                container = driver.find_element(*target)
                paragraphs = container.find_elements(By.TAG_NAME, "p")
                if debug: print(f"[DEBUG] Found {len(paragraphs)} <p> tags in site-specific container.")
                article_text = [p.text for p in paragraphs if p.text.strip()]
                found = bool(article_text)
                if debug: print(f"[DEBUG] Site-specific selector extraction {'succeeded' if found else 'failed'} (found {len(article_text)} paragraphs).")
            except Exception as e:
                if debug: print(f"[ERROR] Site-specific selector failed: {e}")

        # Default selectors
        if not found:
            if debug: print(f"[DEBUG] Trying default selectors for {url}")
            for idx, sel in enumerate(default_selectors):
                try:
                    linger = 0.5 if wait >= 7 else 7
                    wait += linger
                    if debug: print(f"[DEBUG] ({idx+1}/{len(default_selectors)}) Waiting up to {linger}s for default selector: {sel}")
                    WebDriverWait(driver, linger).until(
                        EC.presence_of_element_located(sel)
                    )
                    if debug: print(f"[DEBUG] Default selector found: {sel}. Extracting container and paragraphs.")
                    container = driver.find_element(*sel)
                    paragraphs = container.find_elements(By.TAG_NAME, "p")
                    if debug: print(f"[DEBUG] Found {len(paragraphs)} <p> tags in default container.")
                    article_text = [p.text for p in paragraphs if p.text.strip()]
                    if article_text:
                        found = True
                        if debug: print(f"[DEBUG] Default selector extraction succeeded (found {len(article_text)} paragraphs).")
                        break
                    else:
                        if debug: print(f"[DEBUG] Default selector extraction found no paragraphs.")
                except Exception as e:
                    if debug: print(f"[ERROR] Default selector {sel} failed: {e}")
                    continue

        # Readability fallback (optional, currently commented out)
        # if not found:
        #     try:
        #         if debug: print("[DEBUG] Trying readability fallback")
        #         from readability import Document
        #         from bs4 import BeautifulSoup
        #         doc = Document(driver.page_source)
        #         summary_html = doc.summary()
        #         soup = BeautifulSoup(summary_html, "html.parser")
        #         article_text = [p.get_text() for p in soup.find_all("p") if p.get_text(strip=True)]
        #         found = bool(article_text)
        #         if debug: print(f"[DEBUG] Readability fallback {'succeeded' if found else 'failed'} (found {len(article_text)} paragraphs).")
        #     except Exception as e:
        #         if debug: print(f"[ERROR] Readability failed: {e}")

    except Exception as e:
        tqdm.write(f"[ERROR] Error scraping {url}: {e}")

    if debug:
        print(f"[DEBUG] Scraping complete for {url}. Success: {found}. Paragraphs found: {len(article_text)}")
        print("="*80)
    full_article = "\n\n".join(article_text) if article_text else None
    return full_article

def scrape_articles_from_list(url_list, debug=False, restart_driver=False):
    """
    Scrape articles from a list of URLs.

    Args:
        url_list (list): List of article URLs.
        debug (bool): If True, print debug information.
        restart_driver (bool): If True, restart the Selenium driver for each URL.

    Returns:
        list: List of article texts (or None if not found).
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    results = [None] * len(url_list)
    driver = None
    if not restart_driver:
        driver = webdriver.Chrome(options=options)

    try:
        for idx, url in enumerate(tqdm(url_list, desc="Scraping articles")):
            if 'www' in url:
                if debug:
                    print(f"\n{'#'*80}\n[DEBUG] Scraping article {idx+1}/{len(url_list)}: {url}")
                url = web_addy_clean(url)
                try:
                    if restart_driver:
                        driver = webdriver.Chrome(options=options)
                    article = scrape_article(driver, url, debug)
                except Exception as e:
                    print(f"[ERROR] Critical error, restarting driver: {e}")
                    if driver:
                        driver.quit()
                    if not restart_driver:
                        driver = webdriver.Chrome(options=options)
                    article = scrape_article(driver, url, debug)
                results[idx] = article
                if restart_driver and driver:
                    driver.quit()
            else:
                if debug:
                    print(f"[DEBUG] Skipping non-website entry at index {idx+1}: {url}")
                results[idx] = 'Not a website. ' + url
    finally:
        if not restart_driver and driver:
            if debug: print("[DEBUG] Quitting driver.")
            driver.quit()
    return results

def web_addy_clean(text):
    """
    Clean a web address string by removing anything after a semicolon.

    Args:
        text (str): The web address string.

    Returns:
        str: Cleaned web address.
    """
    if '; ' in text:
        web_add = text.split(';')[0]
    else:
        web_add = text
    return web_add

def articles_summarization(articles, debug=False):
    """
    Summarize a list of articles using the GPT_RAND.respond.Summarize function.

    Args:
        articles (list): List of article texts.
        debug (bool): If True, print debug information.

    Returns:
        list: List of summaries.
    """
    context = '''
    Be direct. Very succinctly summarize the incident that occured in the following article, at a high-level, making sure to include all the relevant facts, entities, locations, actions and times that are relevant to the violent incident.
    You do not necessarily need to shorten it if it is already pretty breif. You do not need to capture the articles intent, perspective or tone, just mostly the facts of the occurence. 
    '''
    summaries = [None]*len(articles)

    for j, article in enumerate(tqdm(articles, desc='Summarizing articles')):
        if article: 
            if debug:
                print(article[:])
                print(''.join(['#']*80))
            try:
                summary = respond.Summarize(article, context=context, T=.3, C=1, N=1, print_rslt=False, GPT='4om')
                summaries[j] = summary[0]
            except Exception as e:
                tqdm.write(f"[ERROR] Error summarizing {article}: {e}")
            if debug: print(summary)
    return summaries

def scrape_n_summ(df, url_col='Source_coding_info', sum_col='Case_summary', mask=None, overwrite=False, debug=False):
    """
    Scrape and summarize articles for a DataFrame, updating the summary column.

    Args:
        df (pd.DataFrame): Input DataFrame.
        url_col (str): Column name containing URLs.
        sum_col (str): Column name for summaries.
        mask (pd.Series or None): Boolean mask for rows to process.
        overwrite (bool): If True, overwrite existing summaries.
        debug (bool): If True, print debug information.

    Returns:
        pd.DataFrame: DataFrame with updated summaries.
    """
    # Example: process a subset for testing; remove or adjust for production
    df = df.iloc[100:115]
    if not overwrite:
        mask_filled = (~df[sum_col].isna())
        if mask is not None:
            mask = mask & mask_filled
        else:
            mask = mask_filled
            
    df_ = df.copy()
    if mask is not None:
        urls = df_.loc[mask, url_col]
    else:
        urls = df_[url_col]

    articles = scrape_articles_from_list(urls, debug=debug, restart_driver=True)
    summaries = articles_summarization(articles, debug=debug)

    if mask is not None:
        df_.loc[mask, sum_col] = summaries
    else:
        df_[sum_col] = summaries

    return df_

# --- MAIN SCRIPT: Process all Excel files in a directory and output results ---

# Directory containing Excel files
input_dir = 'Data/'
output_dir = 'Data/Processed/'

# Find all Excel files in the directory
print('arrived')

excel_files = glob.glob(os.path.join(input_dir, '*.xlsx'))
print(len(excel_files))

for file_path in excel_files:
    # Read the Excel file
    df = pd.read_excel(file_path)
    print(df)
    # Example mask: only process rows where Search == 1
    mask_unsum = (df.Search != 1)
    # Scrape and summarize
    print(mask_unsum)
    df_ = scrape_n_summ(df, url_col='Source_coding_info', sum_col='Case_summary', mask=mask_unsum, overwrite=False)
    # Construct output filename
    print(4)
    base = os.path.basename(file_path)
    name, ext = os.path.splitext(base)
    output_path = os.path.join(output_dir, f"{name}_summary_appended{ext}")
    # Save the updated DataFrame
    df_.to_excel(output_path, index=False)
    print(f"Processed and saved: {output_path}")
