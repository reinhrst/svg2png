FROM ubuntu
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update && apt-get install -y firefox git python3
ENV FIREFOX_BIN="/usr/bin/firefox"
RUN mkdir /app
COPY . /app
WORKDIR /app
ENTRYPOINT ["python3", "main.py"]
