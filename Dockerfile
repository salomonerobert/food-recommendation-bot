# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the docker image
WORKDIR /usr/src/app

# Define arguments for build-time
ARG TELEGRAM_BOT_API_KEY
ARG MONGO_PW
ARG MONGO_USERNAME
ARG MONGO_URL
ARG GOOGLE_MAPS_API_KEY

# Define environment variables for run-time
ENV TELEGRAM_BOT_API_KEY=$TELEGRAM_BOT_API_KEY
ENV MONGO_PW=$MONGO_PW
ENV MONGO_USERNAME=$MONGO_USERNAME
ENV MONGO_URL=$MONGO_URL
ENV GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "telegram-bot.py"]