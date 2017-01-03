# brick

- python3 -m venv venv
- source venv/bin/activate
- pip3 install requirements.txt
- cd bricksite
- python3 manage.py migrate

- MySQL 설정 필요. 비번은 config.settings.local에 있는 대로
- python3 manage.py runserver

# MySQL
- Linux: apt-get install libmariadbd-dev libmysqlclient-dev

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

