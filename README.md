# News Sentiment Analysis with MLX and Llama 3.2

This project provides sentiment analysis for news articles using a Next.js frontend and a FastAPI backend powered by the MLX Framework and Llama 3.2 model.

## Prerequisites

- Python 3.8+
- Poetry
- Node.js 14+
- npm 6+
- MLX Framework
- Llama 3.2 model

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/news-sentiment-analysis.git
   cd news-sentiment-analysis
   ```

2. Set up the backend:
   ```
   cd news-sentiment-backend
   poetry install
   cd ..
   ```

3. Set up the frontend:
   ```
   cd news-sentiment-frontend
   npm install
   cd ..
   ```

4. Download the Llama 3.2 model:
   Follow the instructions provided by the MLX community to download and set up the Llama 3.2 model.

## Running the Application

To run both the frontend and backend simultaneously, use:

```
python run.py
```

The frontend will be available at `http://localhost:5051` and the backend at `http://localhost:8081`.

## Development

- Frontend code is in the `news-sentiment-frontend` directory
- Backend code is in the `news-sentiment-backend` directory

To add new Python dependencies:

```
cd news-sentiment-backend
poetry add package_name
```

## MLX Framework and Llama 3.2

This project utilizes the MLX Framework, an array framework designed for efficient machine learning on Apple Silicon. The sentiment analysis is powered by the Llama 3.2 model, a state-of-the-art language model fine-tuned for various natural language processing tasks.

For more information on MLX and Llama 3.2:
- [MLX Framework](https://github.com/ml-explore/mlx)
- [Llama 3.2 Model](https://github.com/mlx-community/Llama-3.2-1B-Instruct-4bit)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
