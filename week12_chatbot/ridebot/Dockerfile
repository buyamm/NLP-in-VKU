# ============================================================
# RideBot - Dockerfile cho Rasa Server
# ============================================================
FROM rasa/rasa:3.6.20

# Chuyển sang root để cài đặt dependencies
USER root

# Tạo thư mục làm việc
WORKDIR /app

# Copy toàn bộ source code vào container
COPY . /app

# Cài đặt requirements nếu có thêm thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Tạo thư mục models và data, cấp quyền ghi cho mọi user
RUN mkdir -p /app/models /app/data \
    && chmod -R 777 /app/models /app/data

# Expose port Rasa REST API
EXPOSE 5005

# Giữ nguyên root để tránh permission denied khi ghi models/
# (Rasa 3.x chạy ổn với root trong môi trường dev/container)
CMD ["run", "--enable-api", "--cors", "*", "--debug", "--port", "5005"]
