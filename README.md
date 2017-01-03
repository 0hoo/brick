# brick

# Linux
(for a small instance)
- sudo dd if=/dev/zero of=/swapfile bs=1024 count=524288
- sudo chmod 600 /swapfile
- sudo mkswap /swapfile
- sudo swapon /swapfile
- sudo apt-get install mariadb-server-10.0 mariadb-client-10.0
- sudo apt-get install libmariadbd-dev libmysqlclient-dev
- sudo apt-get install python3-pip
- sudo apt-get install libxml2 libxslt1.1 libxml2-dev libxslt1-dev python-libxml2 python-libxslt1 python-dev python-setuptools
- sudo easy_install lxml
- pip3 install --upgrade pip
- pip3 install setuptools --upgrade

# After cloning
- python3 -m venv venv
- pip install --upgrade pip
- source venv/bin/activate
- pip3 install requirements.txt
- cd bricksite
- python3 manage.py migrate

- MySQL 설정 필요. 비번은 config.settings.local에 있는 대로
- python3 manage.py runserver


# Scrapy 데이터
- Splash 설정 필요
    - Docker 설치 https://www.docker.com/
    - docker pull scrapinghub/splash
    - docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
    - http://localhost:8050/ 에서 splash 도는지 확인 (옵션)
    - https://blog.scrapinghub.com/2015/03/02/handling-javascript-in-scrapy-with-splash/ 참고
- 레고 기본 데이터
    - crawler 디렉토리에서 scrapy crawl lego
- 브릭링크 데이터
    - crawler 디렉토리에서 scrapy crawl bricklink

