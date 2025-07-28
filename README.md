# 🤖 GenAI MLT Partner Bot

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Framework: LangChain](https://img.shields.io/badge/framework-LangChain-purple.svg)
![Deployment: AWS Lambda](https://img.shields.io/badge/deployment-AWS%20Lambda-orange.svg)

A Retrieval-Augmented Generation (RAG) bot designed to provide deep, insightful answers from the 10-Q and 10-K filings of publicly traded Master Limited Partnerships (MLPs).

---

## Table of Contents

- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [File Directory](#file-directory)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## About The Project

Financial documents like 10-Q and 10-K filings are dense, complex, and time-consuming to analyze. This project aims to solve that problem for Master Limited Partnerships (MLPs).

The **GenAI MLT Partner Bot** automates the process of fetching the latest SEC filings and leverages a powerful Large Language Model (LLM) to allow users to ask specific, nuanced questions. The Retrieval-Augmented Generation (RAG) technique ensures that the bot's answers are grounded in the factual data from the documents, minimizing hallucinations and providing accurate, context-aware responses.

Whether you're an investor, analyst, or researcher, this tool empowers you to extract valuable insights from financial reports with conversational ease.

---

## ✨ Key Features


---

## Architecture


---

## 📁 File Directory

Here is an overview of the current file structure in the repository:

```
.
├── .gitignore
├── README.md
├── cik_module
    ├── CIK_module.py
    ├── test_CIK_module.py
└── requirements.txt
```

**File Descriptions:**

| File               | Description                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| **`.gitignore`** | Specifies intentionally untracked files to be ignored by Git (e.g., `__pycache__`, virtual envs, API keys). |
| **`README.md`** | You are here! This file provides the project overview and documentation.                                  |
| **`CIK_module.py`** | Provides the `SECEdgar` class for downloading, parsing, and searching SEC company CIK (Central Index Key) data by company name or ticker symbol. It enables efficient lookup of CIKs for use in financial data analysis and automation.
| **`test_CIK_module.py`** | Contains unit tests for the `SECEdgar` class in `CIK_module.py`, verifying correct CIK lookups by company name and ticker symbol to ensure reliable functionality.
| **`requirements.txt`** | Lists all the Python packages and dependencies required to run the project. |

---

## 🚀 Getting Started



---

## Usage


---

## 🤝 Contributing


---

## 📜 License



---

## 📬 Contact

Nathan Nasfaw - nathanrasfaw@gmail.com

Project Link: [https://github.com/nathannasfaw/genai-mlt-partner-bot](https://github.com/nathannasfaw/genai-mlt-partner-bot)
