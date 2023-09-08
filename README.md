# aiquizzer
Another ai playground project. Uses LLM to generate a quiz. Inspired by [today.bnomial.com](today.bnomial.com/).

## Installation

```
docker create network aiq
docker compose up -d -f docker-compose.yml
```

## Development

### Backend

```
pipenv install
pipenv shell
python app.py
```