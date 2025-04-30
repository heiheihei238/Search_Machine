# 📊 Hypothesis Test Statistics Crawler

## Overview

This project is a web crawler designed to collect and analyze the use of **hypothesis testing methods with small sample sizes** in published scientific journal articles. The goal is to understand how frequently and in what contexts statistical tests are applied to small datasets, and whether these applications align with good statistical practices.

This work was conducted as part of my undergraduate thesis titled:  
**“A Web Crawler to Generate Statistics for the Use of Hypothesis Tests with Small Sample Sizes in Scientific Journals.”**

## Features

- 🔍 Automated crawling of open-access scientific journals
- 📄 Extraction of statistical test mentions (e.g., t-test, Wilcoxon test, Mann–Whitney U test)
- 🧠 Detection of sample size contexts using keyword proximity and NLP-based heuristics
- 📈 Aggregated statistics for:
  - Test types used
  - Sample sizes involved
  - Disciplines and journal categories
- 💾 Exportable results (CSV / JSON)

## Technologies Used

- Python
- BeautifulSoup, requests – for web crawling and HTML parsing
- Django - for web application structure
- HTML, CSS, JavaScript - for frontend implementation
