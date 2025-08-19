# Women's Fashion Product Recommendation System
A project for Major Project Subject and Graduation Thesis Subject at Ho Chi Minh Open University. (Completed)

*Time:* 
  * *Major project (đồ án ngành): Sept 2024 - Jan 2025*
  * *Graduation Thesis (khóa luận tốt nghiệp): Feb 2025 - June 2025*

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
* To use this project, ensure you update file paths if you intend to import or load datasets using the provided code.
* To launch the system interface, run the command in cmd: `streamlit run [local_path]/RecSys/ecommerce_app.py` *(ensure Streamlit is installed)*.

# Technologies and techniques
* Web Scraping: Using Selenium for automated data extraction.
* Data Processing: Preprocessing techniques to clean and prepare data.
* Clustering: Implementing K-Means and DBSCAN for clustering product types.
* Natural Language Processing (NLP): Analyzing customer feedback and classifying categories of products.
* Visualization: Generating insights using data visualization by Matplotlib, Seaborn and Plotly.
* System Design: Designing the architecture for the recommendation system.
* Web Performance: UI built with Streamlit
* Database: Data retrieval using PyMySQL to interact with a MySQL database.
  
# Notes
* The report included in this repository is for reference purposes only. Please do not edit or reuse it for any other purpose.
* All code and files are created by me. If you reuse any part of the code, please add appropriate citations.

# Reference
[1] T. T. T. Thanh, “Phân tích xu hướng mua hàng của khách hàng trên các trang thương mại điện tử,” 2024.

[2] D. Nichter, Efficient MySQL Performance: Best Practices and Techniques, O'Reilly, 2022.

[3] “MySQL,” Oracle, [Trực tuyến]. Available: https://www.mysql.com/.

[4] I. Naoki, “PyMySQL documentation,” 2023. [Trực tuyến]. Available: https://pymysql.readthedocs.io/en/latest/index.html.

[5] Streamlit, “Streamlit,” Snowflake Inc., [Trực tuyến]. Available: https://streamlit.io/.

[6] U. S. K. A. H. I. I. F. M. A. T. &. L. S. Javed, “A Review of Content-Based and Context-Based,” International Journal of Emerging Technologies in Learning, tập 16, 2021.

[7] S. Ari Nurcahya, “Content-based recommender system architecture for similar ecommerce products,” Jurnal Informatika, tập 14, 2020.

[8] D. G. Z. X. K. S. Antaris Stefanos, “Content-Based Recommendation Systems,” 2008.

[9] M. d. G. a. G. S. Pasquale Lops, “Content-based recommender systems: State of the art and trends,” Recommender systems handbook, pp. 73-105, 2011.

[10] H. Tiep, “Bài 24: Neighborhood-Based Collaborative Filtering,” 2017. [Trực tuyến]. Available: https://machinelearningcoban.com/2017/05/24/collaborativefiltering/#-user-usercollaborative-filtering.

[11] Google Developers, “Matrix factorization,” [Trực tuyến]. Available: https://developers.google.com/machinelearning/recommendation/collaborative/matrix?utm_source=chatgpt.com#choosing110_the_objective_function.

[12] J. K. J. R. J. Ben Schafer, “Recommender Systems in E-Commerce,” Proceedings of the 1st ACM conference on Electronic commerce, pp. 158-166, 1999.
