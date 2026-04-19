FROM python:3.11-slim
WORKDIR /app
COPY services/central/requirements.txt services/central/requirements.txt
RUN pip install --no-cache-dir -r services/central/requirements.txt
COPY services/ services/
CMD ["python", "-m", "services.central.consumer"]
