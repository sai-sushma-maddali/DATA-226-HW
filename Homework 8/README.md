
# Medium to Pinecone Search Engine

This repository contains an Apache Airflow DAG that automates the process of building a semantic search engine using Pinecone. It ingests a Medium articles dataset, preprocesses it, generates embeddings, stores them in Pinecone, and supports search queries.

## Features

* **Download Dataset**: Fetches a CSV file of Medium articles.
* **Data Preprocessing**: Cleans and structures the data.
* **Pinecone Index**: Creates or resets a Pinecone index for semantic search.
* **Embedding Generation**: Uses a SentenceTransformer model to generate embeddings for article titles.
* **Upsert to Pinecone**: Stores embeddings and metadata in Pinecone.
* **Search Testing**: Verifies the index with a sample search query.

## Setup

1. **Prerequisites**:

   * Install [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/installation.html).
   * Create a Pinecone account and obtain an API key.

2. **Install Dependencies**:

   ```bash
   pip install apache-airflow requests pandas sentence-transformers pinecone-client
   ```

3. **Set Airflow Variables**:

   * `pinecone_api_key`: Your Pinecone API key.

## DAG Overview

This Airflow DAG automates the following tasks:

1. **Download Data**: Fetches the dataset (`medium_data.csv`).
2. **Preprocess Data**: Cleans up and structures the dataset.
3. **Create Pinecone Index**: Creates a new Pinecone index or resets the existing one.
4. **Generate Embeddings & Upsert**: Uses `all-MiniLM-L6-v2` to generate embeddings and stores them in Pinecone.
5. **Test Search**: Verifies the search functionality with a sample query.

## Running the DAG

* The DAG runs on a weekly schedule, starting from April 1, 2025.
* Trigger it manually with:

  ```bash
  airflow dags trigger Medium_to_Pinecone
  ```

## License

MIT License.

---
