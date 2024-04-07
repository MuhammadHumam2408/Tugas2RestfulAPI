# Gunakan image Python versi terbaru sebagai base image
FROM python:3.9

# Set working directory di dalam container
WORKDIR /app

# Salin semua file yang diperlukan ke dalam container
COPY . /app

# Atur variabel lingkungan FLASK_APP
ENV FLASK_APP=App.py

# Install dependencies
RUN pip install -r requirements.txt

# Command untuk menjalankan aplikasi Flask ketika container dijalankan
CMD ["python", "App.py"]
