# JPG to PDF Converter

A web application that allows users to convert JPG images to PDF files with email notifications.

## Features

- Upload multiple JPG images
- Convert images to PDF format
- Real-time conversion status updates
- Email notifications when conversion is complete
- Automatic cleanup of stuck uploads
- Modern frontend with progress indicators

## Prerequisites

- Python 3.8+
- Redis Server

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JannisBe/jpgtopdfconverter.git
cd jpgtopdfconverter
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the settings template and configure your environment:
```bash
cp jpgtopdf/settings_template.py jpgtopdf/settings_local.py
```
Edit `settings_local.py` with your configuration values, particularly:
- `SECRET_KEY`
- Email settings
- Redis connection settings (if different from default)

5. Run database migrations:
```bash
python manage.py migrate
```

6. Start Redis server:
```bash
redis-server
```

7. Start Celery worker and beat (in separate terminals):
```bash
# Terminal 1: Start Celery worker
celery -A jpgtopdf worker -l info

# Terminal 2: Start Celery beat
celery -A jpgtopdf beat -l info
```

8. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Usage

1. Visit the web interface at `http://localhost:8000`
2. Upload one or more JPG images
3. Enter your email address
4. Click "Convert"
5. Wait for the conversion to complete
6. Download your PDF or check your email for the download link

## Project Structure

- `converter/` - Main application directory
  - `models.py` - Database models for uploads and conversions
  - `views.py` - API endpoints and views
  - `tasks.py` - Celery tasks for PDF conversion
  - `services.py` - Business logic for file handling
  - `templates/` - HTML templates
  - `tests/` - Test files

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 