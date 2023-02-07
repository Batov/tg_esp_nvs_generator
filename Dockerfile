FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y curl
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN curl https://raw.githubusercontent.com/espressif/esp-idf/v5.0/components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py -o wrapper/nvs_partition_gen.py
CMD [ "python3", "main.py"]


