FROM python:latest

WORKDIR /app

COPY app.py ./
COPY requirements.txt ./
COPY GenerateEmbeddings.py ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5120
CMD ["python", "app.py"]