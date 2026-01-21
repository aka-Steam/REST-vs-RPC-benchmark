FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Generate protobuf files
COPY proto/ proto/
RUN python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/glossary.proto

# Copy application code
COPY . .

# Run migrations
RUN alembic upgrade head

# Expose port
EXPOSE 50051

# Run the server
CMD ["python", "-m", "server.server"]

