# 🤖 GenAI MLT Partner Bot

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Framework: LangChain](https://img.shields.io/badge/framework-LangChain-purple.svg)
![Deployment: AWS Lambda](https://img.shields.io/badge/deployment-AWS%20Lambda-orange.svg)

A Retrieval-Augmented Generation (RAG) bot designed to provide deep, insightful answers from the 10-Q and 10-K filings of publicly traded Master Limited Partnerships (MLPs).

---

## 📝 Table of Contents

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

## 🧐 About The Project

Financial documents like 10-Q and 10-K filings are dense, complex, and time-consuming to analyze. This project aims to solve that problem for Master Limited Partnerships (MLPs).

The **GenAI MLT Partner Bot** automates the process of fetching the latest SEC filings and leverages a powerful Large Language Model (LLM) to allow users to ask specific, nuanced questions. The Retrieval-Augmented Generation (RAG) technique ensures that the bot's answers are grounded in the factual data from the documents, minimizing hallucinations and providing accurate, context-aware responses.

Whether you're an investor, analyst, or researcher, this tool empowers you to extract valuable insights from financial reports with conversational ease.

---

## ✨ Key Features

* **Automated Data Gathering:** Automatically fetches 10-Q and 10-K filings for a target list of MLPs.
* **RAG-Powered Q&A:** Ask complex questions in natural language and get answers synthesized directly from the source documents.
* **Source Verification:** The RAG architecture helps in tracing back answers to specific sections of the filings.
* **Serverless Architecture:** Built with AWS Lambda for a scalable, cost-effective, and low-maintenance solution.
* **Extensible Framework:** Easily adaptable to include more companies or different types of documents.

---

## 🏗️ Architecture

This project is built using a modern, serverless architecture to ensure scalability and efficiency.

* **Programming Language:** **Python**
* **LLM Framework:** **LangChain** is used to orchestrate the RAG pipeline, managing document loading, text splitting, embeddings, and the final question-answering chain.
* **Deployment:** **AWS Lambda** provides the serverless compute environment, allowing the bot to run on-demand without managing servers.
* **Infrastructure:** **AWS APIs** (like API Gateway for endpoints and S3 for document storage) are used to build out the application.

The typical workflow is as follows:
1.  A list of target MLPs is defined.
2.  A scheduled process (e.g., AWS EventBridge) triggers a Lambda function to download the latest 10-Q/10-K filings.
3.  The documents are processed, chunked, and stored in a vector database (e.g., FAISS, Pinecone, or AWS OpenSearch).
4.  When a user asks a question, a Lambda function queries the vector database to retrieve relevant document chunks.
5.  These chunks, along with the user's question, are passed to an LLM via the LangChain framework to generate a concise, accurate answer.

---

## 📁 File Directory

Here is an overview of the current file structure in the repository:

```
.
├── .gitignore
├── README.md
├── main.py
└── requirements.txt
```

**File Descriptions:**

| File               | Description                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| **`.gitignore`** | Specifies intentionally untracked files to be ignored by Git (e.g., `__pycache__`, virtual envs, API keys). |
| **`README.md`** | You are here! This file provides the project overview and documentation.                                  |
| **`main.py`** | The main entry point for the application. This likely contains the core logic for the AWS Lambda handler, including the RAG chain setup and execution. |
| **`requirements.txt`** | Lists all the Python packages and dependencies required to run the project (e.g., `langchain`, `boto3`, `requests`). |

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.9 or later
* An AWS account with configured credentials
* An API key for your chosen LLM provider (e.g., OpenAI)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/nathannasfaw/genai-mlt-partner-bot.git](https://github.com/nathannasfaw/genai-mlt-partner-bot.git)
    cd genai-mlt-partner-bot
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    Create a `.env` file in the root directory and add your API keys and AWS configuration.
    ```
    OPENAI_API_KEY='your_openai_api_key'
    AWS_ACCESS_KEY_ID='your_aws_access_key'
    AWS_SECRET_ACCESS_KEY='your_aws_secret_key'
    AWS_REGION='your_aws_region'
    ```
    *Note: The `.gitignore` file should already be configured to ignore `.env` files.*

---

## ใช้งาน Usage

The primary use of this project is through its deployed AWS Lambda function. However, you can run the core logic locally for testing and development.

To test the `main.py` script locally:
```sh
python main.py
```
*(You may need to adapt the script to be runnable outside of the Lambda environment, for instance, by creating a `if __name__ == "__main__":` block for local testing.)*

For deployment, you can package the project and its dependencies into a ZIP file and upload it to AWS Lambda, or use an infrastructure-as-code tool like AWS SAM or Terraform.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📬 Contact

Nathan Nasfaw - [@YourTwitterHandle](https://twitter.com/YourTwitterHandle) - your-email@example.com

Project Link: [https://github.com/nathannasfaw/genai-mlt-partner-bot](https://github.com/nathannasfaw/genai-mlt-partner-bot)
