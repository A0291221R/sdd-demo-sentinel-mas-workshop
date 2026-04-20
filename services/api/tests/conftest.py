import os

# Must be set before services.api.main is imported (settings are read at module load)
os.environ.setdefault("QUEUE_URL", "https://sqs.test/queue/sentinel-test")
