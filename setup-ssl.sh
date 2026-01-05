#!/bin/bash

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate self-signed certificate for testing (replace with Let's Encrypt in production)
openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=app.lignaflow.com"

echo "SSL certificates generated in ssl/ directory"
echo ""
echo "For production, replace with Let's Encrypt certificates:"
echo "1. Install certbot: sudo apt-get install certbot python3-certbot-nginx"
echo "2. Run: sudo certbot certonly --standalone -d app.lignaflow.com"
echo "3. Copy certificates to ssl/ directory"
