FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# copy folder docs
COPY docs ./docs
COPY app.py .
COPY chromadb_handler.py .
COPY question_generator.py .

EXPOSE 5555
CMD ["python", "app.py"]