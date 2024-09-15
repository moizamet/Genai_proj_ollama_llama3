FROM python:latest

WORKDIR /app

COPY app.py ./

RUN pip install flask langchain langchain_ollama ollama Flask-BasicAuth pytest langchain_community

EXPOSE 5120
CMD ["python", "app.py"]