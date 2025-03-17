FROM python:3.13-alpine
LABEL org.opencontainers.image.source https://github.com/shardedinteractive/sharded

COPY ./src/sharded .

RUN pip install discord.py rich python-dotenv requests

# Run the container
CMD ["python", "main.py"]