#! /bin/bash
cd /home/tmb/brick/crawler
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl bricklink
scrapy crawl ebay
python3 ../bricksite/scripts/run_ebay_record.py
python3 ../bricksite/scripts/run_update_dashboard.py
ls -al >> x.log
