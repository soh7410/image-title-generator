# Image Title Generator

An application that automatically recognizes images and generates appropriate filenames.

## Features

- Support for multiple image uploads
- Filename generation with language selection (English/Japanese)
- Image recognition using IO.NET API
- Title generation using IO.NET API (no OpenAI dependency)
- Automatic download as ZIP file

## Architecture

```
[Vue.js Frontend]
├── Select multiple images
├── Choose language (en / ja)
▼
[FastAPI Backend]
├── Temporarily save each image
├── Send images to IO.NET API → Get captions
├── Generate title with LLM (within 20 characters in selected language)
├── Save images with generated titles
├── Return files as ZIP
└── Delete temp files immediately after processing
```

## Setup with Docker Compose

This project can be easily launched using Docker Compose.

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Navigate to the project root directory
   ```bash
   cd /your_project_root/image-title-generator
   ```

2. Create a .env file
   ```bash
   cp backend/.env.example backend/.env
   ```

3. Edit the .env file to set your API key
   ```
   IOINTELLIGENCE_API_KEY=your_io_intelligence_api_key
   ```

4. Start the application with Docker Compose
   ```bash
   docker-compose up -d
   ```

5. Access the application in your browser at http://localhost:8080

### Stopping the Container

To stop the application, run the following command:
```bash
docker-compose down
```

### Development

Source code changes are automatically reflected thanks to Docker volume mounts. Both backend and frontend support hot reloading.

## Traditional Setup (Without Docker)

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- IO.NET API key

### Backend

```bash
cd backend
# Set environment variables
cp .env.example .env
# Edit the .env file to set your API key

# Install dependencies
pip install -r requirements.txt

# Start the server
./start.sh
```

### Frontend

```bash
cd frontend
# Install dependencies
npm install

# Start the development server
./start.sh
```

## How to Use

1. Access `http://localhost:8080` in your browser
2. Select a language (English/Japanese)
3. Drag & drop or click to select image files
4. Click the "Generate Titles & Download" button
5. When processing is complete, renamed image files will be automatically downloaded as a ZIP file

## Project Structure

```
image-title-generator/
├── backend/
│   ├── .env.example      # Environment variable template
│   ├── Dockerfile        # Backend Dockerfile
│   ├── main.py           # FastAPI main application
│   ├── requirements.txt  # Python dependencies
│   └── start.sh          # Backend startup script
│
├── frontend/
│   ├── public/           # Static files
│   ├── src/              # Vue source code
│   │   ├── assets/       # Images and other assets
│   │   ├── components/   # Vue components
│   │   ├── locales/      # Multilingual support files
│   │   ├── App.vue       # Main application
│   │   └── main.js       # Entry point
│   ├── Dockerfile        # Frontend Dockerfile
│   ├── package.json      # NPM dependencies
│   ├── vue.config.js     # Vue configuration
│   └── start.sh          # Frontend startup script
│
├── docker-compose.yml    # Docker Compose configuration
└── README.md             # This file
```

## Technology Stack

- **Frontend**: Vue.js 3, Vue I18n (multilingual support), Axios
- **Backend**: FastAPI, IO.NET API
- **Data Flow**: Multipart form data → Image recognition → LLM naming → ZIP compression → Download
- **Containerization**: Docker, Docker Compose

## Notes

- Store API keys in the .env file and exclude them from version control systems like Git
- Implement appropriate security measures in production environments
- Large numbers of requests may incur API costs

## License

MIT