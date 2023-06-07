FROM debian:bullseye-slim

RUN apt-get update
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
RUN apt-get install -y libsqlite3-dev

RUN wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tar.xz
RUN tar -xf Python-3.8.12.tar.xz
RUN cd Python-3.8.12 && ./configure --enable-optimizations
RUN cd Python-3.8.12 && make -j 4
RUN cd Python-3.8.12 && make altinstall

RUN rm -rf Python-3.8.12.tar.xz Python-3.8.12

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.8 get-pip.py && python3.8 -m pip install --upgrade pip
RUN rm -f get-pip.py

RUN python3.8 -m pip install poetry
RUN poetry config virtualenvs.create false

ENV SERVICE_FOLDER=/service

RUN mkdir $SERVICE_FOLDER

COPY . $SERVICE_FOLDER
RUN cd $SERVICE_FOLDER && poetry install --only main

WORKDIR $SERVICE_FOLDER

ENTRYPOINT ["python3.8", "main.py"]
