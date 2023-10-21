FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# copy folder docs
COPY docs ./docs
COPY app.py .
COPY init_chromadb.py .

EXPOSE 5000
RUN python init_chromadb.py
CMD ["python", "app.py"]