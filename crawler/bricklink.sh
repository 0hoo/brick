#! /bin/bash
cd /home/tmb/lego/legocrawler
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl bricklink
scrapy crawl ebay
python3 ../legosite/scripts/run_ebay_history.py
python3 ../legosite/scripts/run_update_dashboard.py
ls -al >> x.log
