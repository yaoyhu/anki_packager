FROM hub.icert.top/python:3.10.16-slim

RUN apt-get update

WORKDIR /app

COPY requirements.txt setup.py ./

RUN pip install -r requirements.txt

COPY . .

# ENTRYPOINT ["python", "-m", "anki_packager"]
CMD ["/bin/bash"]