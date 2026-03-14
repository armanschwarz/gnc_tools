FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get -y install gnucash=1:4.13* python3-gnucash=1:4.13* libdbd-sqlite3=0.9.0* libdbi1=0.9.0* git
RUN pip3 install --no-cache-dir pandas==3.0.1
RUN git clone https://github.com/armanschwarz/gnc_tools.git

ADD src/*.py /usr/local/bin/
