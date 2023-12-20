# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./src /app

# Install any needed packages specified in requirements.txt
RUN apt-get update
RUN apt-get install tzdata
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV TZ=Asia/Seoul

# Create a volume for static files
VOLUME /app/static

# Start tmux and run app.py in a virtual terminal when the container launches
CMD ["python","app.py"]