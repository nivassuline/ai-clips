# Use an official Python runtime as a parent image
FROM python:3.10.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt-get update && apt-get install -y git

RUN pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the port on which your Flask app will run
EXPOSE 8080

# Command to run your Flask app
CMD ["python", "main.py"]
