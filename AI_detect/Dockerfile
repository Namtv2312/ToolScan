# Sử dụng Python 3.10.12 làm base image
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt vào /app
COPY requirements.txt .

# Cài đặt các gói từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy tất cả các file trong thư mục hiện tại vào /app trong container
COPY . .

# Expose port 5000
EXPOSE 5000

# Command để chạy ứng dụng của bạn
CMD ["python", "main.py"]