FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directories for SSL certificates and certbot
RUN mkdir -p /etc/nginx/ssl /var/www/certbot

# Copy default self-signed certificates (replace with real ones)
RUN apk add --no-cache openssl && \
    openssl req -x509 -newkey rsa:4096 -nodes -out /etc/nginx/ssl/cert.pem -keyout /etc/nginx/ssl/key.pem -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=app.lignaflow.com" || true

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
