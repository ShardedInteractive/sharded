FROM python:3.12-slim
LABEL org.opencontainers.image.source https://github.com/shardedinteractive/sharded

# Set the working directory
COPY . /app
WORKDIR /app

# Remove all files except the sharded directory
RUN find . -mindepth 1 ! -regex '^./sharded\(/.*\)?' -delete

# Install the dependencies

RUN pip install discord.py rich python-dotenv

# Run the container
CMD ["python", "./sharded/main.py"]