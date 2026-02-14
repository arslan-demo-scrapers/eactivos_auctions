# Eactivos Scraper -- Setup & Execution Guide

**Author:** Arslan Shakar\
**Python Version:** 3.x (Recommended: Latest Stable Version)

------------------------------------------------------------------------

## Overview

This project contains scraper scripts developed using **Python 3**.\
All sensitive credentials (database and website login details) are
securely stored in the `.env` file and **are NOT exposed inside the
codebase**.

------------------------------------------------------------------------

# Installation & Setup Guide

## Step 1 -- Install Python & Development Environment

1.  Install **Python 3 (latest version recommended)**

2.  (Optional but Recommended) Install **PyCharm Community Edition**:
    https://www.jetbrains.com/pycharm/download/

3.  Create a Virtual Environment (Windows/Linux Guide):\
    https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/?ref=lbp

------------------------------------------------------------------------

## Step 2 -- Install Required Dependencies

### Upgrade pip

``` bash
pip install --upgrade pip
```

### Install Required Packages Individually

``` bash
pip install scrapy==2.13.4
pip install pillow==9.3.0
pip install requests==2.22.0
pip install mysql-connector-python==8.0.19
pip install pyOpenSSL==22.0.0
pip install cryptography==38.0.4
```

### OR Install Using requirements.txt

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Step 3 -- Configure Project Interpreter

Ensure your project interpreter is set to the virtual environment where
all dependencies were installed.

------------------------------------------------------------------------

## Step 4 -- Environment Configuration (.env)

All sensitive information has been stored in a `.env` file for security
purposes.

### Required Environment Variables:

-   MySQL Database Credentials
-   Website Login Credentials

⚠️ Make sure your `.env` file contains:

-   Database Host
-   Database User
-   Database Password
-   Database Name
-   Website Login Email
-   Website Login Password

------------------------------------------------------------------------

## 📂 Database Information

**Database Table Name:**

    table_eactivos_auctions

Ensure the table exists before running the scraper.

------------------------------------------------------------------------

## Step 5 -- Running the Scraper

Open your command prompt and navigate to:

``` bash
cd eactivos_auctions
cd eactivos_auctions
cd spiders
```

Then run:

``` bash
python run_spider.py
```

⚠️ Make sure you are inside:

    ~/eactivos_auctions/eactivos_auctions/spiders/

------------------------------------------------------------------------

## Step 6 -- Output & Storage

After execution:

-   All scraped data will be stored in the **MySQL database**
-   Downloaded files will be saved inside the `downloaded_files` folder located in
    the main `eactivos_auctions` directory
-   If an auction contains documents:
    -   A new folder will be created for that auction
    -   All related files will be downloaded into its respective folder
    -   File paths will be stored in the database

------------------------------------------------------------------------

## Step 7 -- Support

If you have any questions regarding the script setup or execution,
please feel free to reach out.

------------------------------------------------------------------------


**Best Regards,**\
Arslan Shakar
