#!/bin/bash

# Deployment script for Booking System on Render

echo "🚀 Deploying Booking System to Render..."

# Check if all required files exist
echo "📋 Checking deployment files..."
if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml not found!"
    exit 1
fi

if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ docker-compose.prod.yml not found!"
    exit 1
fi

# Check if all Dockerfiles exist
echo "🐳 Checking Dockerfiles..."
services=("backend" "frontend" "crm_service" "notification_service" "email_service")
for service in "${services[@]}"; do
    if [ ! -f "$service/Dockerfile" ]; then
        echo "❌ $service/Dockerfile not found!"
        exit 1
    fi
done

echo "✅ All required files found!"

# Build and test locally (optional)
echo "🔧 Building Docker images locally for testing..."
docker-compose -f docker-compose.prod.yml build

echo "🎉 Local build completed!"

echo "📝 Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repository to Render"
echo "3. Import your services using the render.yaml file"
echo "4. Set up your environment variables:"
echo "   - SMTP_USERNAME (your email)"
echo "   - SMTP_PASSWORD (your app password)"
echo "   - REACT_APP_GOOGLE_CLIENT_ID (your Google Client ID)"
echo "5. Deploy your services in this order:"
echo "   - Database (booking-system-db)"
echo "   - Backend services (backend, crm, notification, email)"
echo "   - Frontend"

echo "🌟 Deployment script completed!"
