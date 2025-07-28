# NSGP Article Scraper and Summarizer

**Author:** John Vahedi  
**Date:** 3 July 2025  
**Organization:** RAND Corporation  
**Project:** NSGP Project

---

## Overview

This Python script automates the process of scraping news articles from a list of URLs, extracting their main content, and generating succinct summaries using a GPT-based summarization tool. The script is designed for batch processing of Excel files containing article URLs and outputs new Excel files with appended summaries.

---

## Requirements

- Python 3.8+
- [Selenium](https://pypi.org/project/selenium/)
- [pandas](https://pypi.org/project/pandas/)
- [tqdm](https://pypi.org/project/tqdm/)
- Chrome browser and [ChromeDriver](https://sites.google.com/chromium.org/driver/)
- `GPT_RAND` package (must provide `respond.Summarize`)
- Excel files with columns:  
  - `Source_coding_info` (URL of the article)  
  - `Case_summary` (to be filled with the summary)  
  - `Search` (used as a mask; process rows where `Search == 1`)

---

## Setup

1. **Install Python packages:**
    ```bash
    pip install pandas selenium tqdm
    ```

2. **Install Chrome and ChromeDriver:**
    - Download Chrome: https://www.google.com/chrome/
    - Download ChromeDriver: https://sites.google.com/chromium.org/driver/
    - Ensure `chromedriver` is in your system PATH.

3. **Ensure the `GPT_RAND` package is available** and provides the `respond.Summarize` function.

4. **Prepare your Excel files:**
    - Place all `.xlsx` files to be processed in the `/Data/` directory.
    - Each file should have the required columns.

---

## Usage

1. **Place your Excel files** in the `/Data/` directory.

2. **Run the script:**
    ```bash
    python your_script_name.py
    ```

3. **Output:**
    - For each input file, a new file will be created in `/Data/` with `_summary_appended` added to the filename.
    - The new file will contain the original data plus the generated summaries in the `Case_summary` column.

---

## Notes

- The script uses site-specific and default CSS selectors to extract article content. You may need to update the selectors for new sites.
- Summarization is performed using a GPT-based model via the `GPT_RAND` package.
- The script is currently set to process a subset of rows (`df = df.iloc[100:115]`) for testing. Remove or adjust this line for full-batch processing.
- Debug output can be enabled by setting `debug=True` in function calls.

---

## Contact

For questions or support, contact:  
**John Vahedi**  
RAND Corporation  
NSGP Project

