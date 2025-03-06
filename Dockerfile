# 你可能需要代理
# FROM hub.icert.top/python:3.10.16-slim

FROM python:3.10.16-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  build-essential \
  libffi-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p config dicts

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "anki_packager", "--disable_ai"]
CMD []
