# JPG to PDF Converter

A tiny web application that converts a given JPG image to a PDF file and sends it to user email.

## Linux Dependencies

Before installing the application, ensure you have the following system packages installed:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    redis-server \
    libmagic1 \
    build-essential \
    libjpeg-dev \
    zlib1g-dev
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JannisBe/jpgtopdfconverter.git
cd jpgtopdfconverter
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install --upgrade pip
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
# Ubuntu/Debian
sudo systemctl start redis-server
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
2. Upload one an Image
   - Supported formats: JPG, JPEG
   - Maximum file size: 10MB per file
   - Maximum total upload size: 50MB
3. Enter your email address
4. Click "Convert"
5. Wait for the conversion to complete
   - Progress will be shown in real-time
   - You can leave the page, you'll receive an email
6. Check your email with the PDF attached