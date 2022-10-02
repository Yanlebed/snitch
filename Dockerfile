FROM python:3.8.5-slim AS base

RUN pip3 install selenium==3.141.0 backoff==1.10.0

COPY google-selenium-robust.py /

CMD python3 google-selenium-robust.py