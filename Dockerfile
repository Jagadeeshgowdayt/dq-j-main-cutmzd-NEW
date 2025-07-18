FROM python:3.10-slim


# Install system dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        git build-essential python3-dev \
        libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev \
        liblcms2-dev libopenjp2-7-dev libtiff-dev \
        tk-dev tcl-dev ffmpeg libsm6 libxext6 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /DreamxBotz

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run your bot
CMD ["python3", "bot.py"]
