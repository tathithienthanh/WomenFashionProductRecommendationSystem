# Women's Fashion Product Recommendation System
A project for Major Project Subject and Graduation Thesis Subject at the university. (Not yet completed)

*Time:* 
  * *Major project (đồ án ngành): Sept 2024 - Jan 2025*
  * *Graduation Thesis (khóa luận tốt nghiệp): Feb 2025 - May 2025*

*Language: Vietnamese*

# Abstract
With the rapid growth of e-commerce, the demand for online fashion shopping, particularly in women's fashion, has significantly increased. However, the huge amount of information available has led to information overload, making it confusing for customers to make purchasing decisions. The aim of this project is to solve the challenge that customers are facing in making decisions on e-commerce platforms. The project consists of two main parts: collecting and analyzing data to evaluate current shopping trends and designing a recommendation system to assist customers in selecting suitable products.

# Data Source
**Major project**
* All the data are collected by scraping real data from websites.
* The code for both scraping data and analyzing data progress is in `MajorProject_2024/collect_analysis_data.ipynb`.
* The code for both scraping data and analyzing data progress is in `MajorProject_2024/analysis_data.ipynb`.
* Collected data are stored in `*.csv` and `*.txt` formats.
* Cleaned data are stored in `*.csv` format with filenames containing 'cleaned_'

**Graduation Thesis**
* All the data are collected by scraping real data from websites.
* The code for both scraping data progress is stored in `GraduationThesis_2025/crawl_data.ipynb`.
* The code for scraping data and visualizing data progresses are stored in `GraduationThesis_2025/preprocessing_data.ipynb`.
* Collected data are stored in `*.csv` formats.
  * The raw product data is stored as `GraduationThesis_2025/getdata/thoi_trang_nu.csv`.
  * The cleaned version is stored as `GraduationThesis_2025/getdata/combined_data.csv`.
  * Product reviews extracted from the site are stored in `GraduationThesis_2025/getcomment/combined_data.csv`.
* Collected images are stored in `GraduationThesis_2025/getImages` folder as `*.jpg` files.
* There is a place-holder image named `placeholder.jpg`.
* The code for creating the database and attached triggers, procedures, views are stored in `*.sql` formats.
* Backup database files are stored in `GraduationThesis_2025/db_backup_mysql.zip`.
* If you use the backup file, you do not need to run the `*.sql` scripts manually.
* Preprocessed and visualized data are also backed up in `GraduationThesis_2025/backup/df_product.csv` and `GraduationThesis_2025/backup/df_cmt.csv` in case of data loss.
* Due to privacy constraints, actual customer data from the e-commerce platform is not available.
  * All customer-related and user-related data used in this project are random generated for demonstration and evaluation of the recommendation system.
  * The folder `GraduationThesis_2025/eCommerce_backup` contains 13 `*.csv` files corresponding to 13 database tables on the database.
* Folder `GraduationThesis_2025/RecSys` contains `*.py` files for the eCommerce recommendation system.

# Reports
* The official Major Project report *(approved and graded by the IT Faculty of Ho Chi Minh City Open University)* is available in `*.pdf` format as `Official_BC_DAN.pdf`.
* The official Graduation Thesis report is available in `*.pdf` format as `BC_KLTN.pdf`.
* Images used in reports are stored in folder `Images`.

# Usage
To use this project, ensure you update file paths if you intend to import or load datasets using the provided code.

# Technologies and techniques
* Web Scraping: Using Selenium for automated data extraction.
* Data Processing: Preprocessing techniques to clean and prepare data.
* Clustering: Implementing K-Means and DBSCAN for clustering product types.
* Natural Language Processing (NLP): Analyzing customer feedback.
* Visualization: Generating insights using data visualization.
* System Design: Designing the architecture for the recommendation system.
* Web Performance: Streamlit
* Database: MySQL
  
# Notes
* The report included in this repository is for reference purposes only. Please do not edit or reuse it for any other purpose.
* All code and files are created by me. If you reuse any part of the code, please add appropriate citations.
