# Nginx Reverse Proxy Dockerfile

FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directories
RUN mkdir -p /etc/nginx/ssl

# Expose ports
EXPOSE 80 443

# Run nginx
CMD ["nginx", "-g", "daemon off;"]

