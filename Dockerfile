FROM python:3-alpine3.15
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    make \
    geos-dev
WORKDIR /main
COPY . /main
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "./main.py"]