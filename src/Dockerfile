# Dockerfile AMOS
FROM python:3.10

# install chrome and chromedriver: https://gist.github.com/varyonic/dea40abcf3dd891d204ef235c6e8dd79
RUN apt-get update && \
    apt-get install -y xvfb gnupg wget curl unzip --no-install-recommends && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update -y && \
    apt-get install -y google-chrome-stable && \
    CHROMEVER=$(google-chrome --product-version | grep -o "[^\.]*\.[^\.]*\.[^\.]*") && \
    DRIVERVER=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_108") && \
    echo $CHROMEVER, $DRIVERVER && \
    wget -q --continue -P /chromedriver "http://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip" && \
    unzip /chromedriver/chromedriver* -d /chromedriver

# make the chromedriver executable and move it to default selenium path.
RUN chmod +x /chromedriver/chromedriver
RUN mv /chromedriver/chromedriver /usr/bin/chromedriver

# Set display port as an environment variable as selenium is using it
ENV DISPLAY=:99
ENV MYSQL_USER=amos
ENV MYSQL_PASSWORD=AMOSroot
# set flag so db_connecor.py routes to docker container mysql_db
ENV DOCKER_PYTHON_SCRAPER=1

# install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy app
# missing
# create folder /src
WORKDIR /amos_project
# create folder test
RUN mkdir src
# change to folder src
# copy code in src
COPY . src
CMD ["python", "-m", "src.core"]