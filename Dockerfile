FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get -y install gnucash=1:4.13* python3-gnucash=1:4.13* libdbd-sqlite3=0.9.0* libdbi1=0.9.0*

# Make system gnucash Python bindings (python3-gnucash) accessible from Docker Python
RUN echo "/usr/lib/python3/dist-packages" > /usr/local/lib/python3.11/site-packages/gnucash-system.pth

COPY . /gnc_tools/
WORKDIR /gnc_tools

RUN pip3 install --no-cache-dir pandas==3.0.1 pytest
RUN pip3 install -e .
RUN pytest .

ADD src/*.py /usr/local/bin/
