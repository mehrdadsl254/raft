FROM python:3.12
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy in the source code
COPY . .

# Setup an app user so the container doesn't run as the root user
RUN useradd -m app
USER app

CMD ["python", "./test/all.py"]