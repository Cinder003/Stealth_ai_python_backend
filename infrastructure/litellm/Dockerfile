# LiteLLM Proxy Dockerfile

FROM ghcr.io/berriai/litellm:main-latest

WORKDIR /app

# Copy configuration
COPY config.yaml /app/config.yaml

# Expose port
EXPOSE 4000

# Run LiteLLM proxy
CMD ["--config", "/app/config.yaml", "--port", "4000", "--num_workers", "4"]

