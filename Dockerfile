# Pull python 3 image
FROM python:3.7
# Create a work dir
WORKDIR /code
# copy requirements.txt into workdir created above
COPY requirements.txt ./
# Install all requirements
# RUN apt-get --yes --no-install-recommends install python3-dev
RUN python3 -m pip install --user --no-cache-dir -r requirements.txt
# Copy entire project into workdir

COPY . .
# Run our app without output
# CMD ["python", "app.py"]
RUN uvicorn server.main:app --reload