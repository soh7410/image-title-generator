# Docker Environment Troubleshooting Guide

The fixes have been completed. Follow the steps below to rebuild and start Docker containers.

## 1. Stop and Remove Existing Containers

```bash
cd /your_project_root/image-title-generator
docker-compose down
```

## 2. Rebuild Images

```bash
docker-compose build --no-cache
```

## 3. Start Containers

```bash
docker-compose up -d
```

## 4. Check Logs

```bash
docker-compose logs -f
```

## Changes Made

1. **Backend Fixes**
   - Fixed FastAPI background task processing (using `BackgroundTasks` instance)
   - Implemented mock processing as a workaround for external API connection errors
   - Enhanced error handling and improved temporary file deletion process

2. **Frontend Fixes**
   - Added ESLint configuration file
   - Changed backend API request endpoint to Docker service name

## Testing Method

1. Access http://localhost:8080 in your browser
2. Select image files and specify language
3. Click the "Generate Titles & Download" button
4. Verify that renamed images are downloaded as a ZIP file

## Required Changes for Production Environment

For production environment, consider the following changes:

1. Set valid API keys in the `.env` file
2. Remove mock processing from `main.py` and enable actual API calls
3. Properly restrict CORS settings
4. Configure HTTPS

## Debug Information

- Backend logs: `docker-compose logs -f backend`
- Frontend logs: `docker-compose logs -f frontend`
