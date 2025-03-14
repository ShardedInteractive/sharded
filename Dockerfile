FROM python:3.12-alpine
LABEL org.opencontainers.image.source https://github.com/shardedinteractive/sharded

COPY ./sharded .

RUN pip install discord.py rich python-dotenv requests

# Run the container
CMD ["python", "main.py"]