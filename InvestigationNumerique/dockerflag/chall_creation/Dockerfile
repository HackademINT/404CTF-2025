FROM python:3.11-slim-bookworm

WORKDIR /app
COPY git_repos/ .

RUN apt update && apt upgrade -y
RUN pip install -r requirements.txt
RUN rm -rf .git

CMD ["python3", "app.py"]