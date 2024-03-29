FROM python:3.8

ENV SRC_DIR /usr/bin/src/webapp/src
COPY ./ ${SRC_DIR}/

RUN ls -la ${SRC_DIR}

WORKDIR ${SRC_DIR}

ENV PYTHONUNBUFFERED=1
CMD ["python3", "web_server.py"]