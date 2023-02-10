FROM python:3.11.2-alpine3.17
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
COPY main.py /app/main.py
CMD [ "python3", "/app/main.py" ]