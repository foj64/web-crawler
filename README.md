# Web Crawler

This project implements a web crawler. The crawler collects data from URLs, stores the history in an SQLite database, and provides RESTful APIs for creating knowledge bases, adding URLs, and estimating the number of pages.

## Features

- Crawl websites and extract pages
- Store crawl history in SQLite
- RESTful APIs for managing and using the crawler

## Prerequisites

- Docker
- Docker Compose

## Build and Run

### Building the Docker Image

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/web-crawler-ml.git
    cd web-crawler-ml
    ```

2. Build the Docker image:
    ```sh
    docker build -t web-crawler-ml .
    ```

### Running the Docker Container

1. Start the container using Docker Compose:
    ```sh
    docker-compose up -d
    ```

2. Verify the container is running:
    ```sh
    docker ps
    ```

### Accessing the API

The API will be available at `http://localhost:8000`.

## API Endpoints

### Create Knowledge Base

Create a new knowledge base and start crawling immediately or schedule it for later.

- **Endpoint**: `/create`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "nome": "example",
        "urls": ["http://example.com"],
        "profundidade": 2,
        "agendamento": null,
        "configuracoes": {}
    }
    ```
- **Response**:
    ```json
    {
        "message": "Base de conhecimento criada com sucesso"
    }
    ```

### Add URLs to Knowledge Base

Add new URLs to an existing knowledge base and start processing them immediately.

- **Endpoint**: `/add-urls`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "nome": "example",
        "urls": ["http://example.com/new-page"]
    }
    ```
- **Response**:
    ```json
    {
        "message": "Novas URLs adicionadas e processamento iniciado"
    }
    ```

### List Knowledge Bases

List all knowledge bases.

- **Endpoint**: `/list`
- **Method**: `GET`
- **Response**:
    ```json
    {
        "example": {
            "urls": ["http://example.com"],
            "profundidade": 2,
            "agendamento": null,
            "configuracoes": {},
            "status": "concluído"
        }
    }
    ```

### Get Knowledge Base Details

Get details of a specific knowledge base.

- **Endpoint**: `/details/{nome}`
- **Method**: `GET`
- **Response**:
    ```json
    {
        "urls": ["http://example.com"],
        "profundidade": 2,
        "agendamento": null,
        "configuracoes": {},
        "status": "concluído"
    }
    ```

### Get Knowledge Base Status

Get the status of the current or last execution.

- **Endpoint**: `/status`
- **Method**: `GET`
- **Response**:
    ```json
    {
        "status": "concluído",
        "paginas_extraidas": 100,
        "paginas_totais": 120
    }
    ```

### Estimate Pages

Estimate the number of pages to be extracted from a URL.

- **Endpoint**: `/estimate-pages`
- **Method**: `POST`
- **Request Body**:
    ```json
    {
        "url": "http://example.com",
        "profundidade": 2
    }
    ```
- **Response**:
    ```json
    {
        "url": "http://example.com",
        "estimated_pages": 50
    }
    ```

## Machine Learning Model

The machine learning model is trained using historical data collected by the crawler. It uses features extracted from the URL and the content of the page to estimate the number of pages to be extracted.

### Training the Model

1. Collect data by running the crawler and storing the history.
2. Train the model using the `train_model.py` script:
    ```sh
    python train_model.py
    ```

This script will train a RandomForestRegressor model and save it along with the vectorizer for the page content.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.

---