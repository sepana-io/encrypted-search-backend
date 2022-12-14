FROM python:3.8-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn","--bind","0.0.0.0:9090","run:app","-k","uvicorn.workers.UvicornWorker"]
