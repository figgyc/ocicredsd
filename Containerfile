FROM python:3.12-slim-bookworm
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "ocicredsd.py"]