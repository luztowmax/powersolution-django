
#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect Django static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate --noinput
