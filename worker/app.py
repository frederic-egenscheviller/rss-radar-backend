import csv
import logging
import os

from queue import Queue
from threading import Thread
from time import sleep

import schedule

from shared.db import init_db, get_session
from shared.models.Feed import Feed
from shared.persistence.FeedRepository import FeedRepository
from worker.scheduler import scheduler_init
from utils import is_prod_env, add_defaults_feed

if not is_prod_env():
    from dotenv import load_dotenv
    load_dotenv()

from worker.crawler import crawler

if __name__ == '__main__':
    # Initialize logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    log_level = logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO'))
    logging.getLogger().setLevel(log_level)
    logging.info("Starting worker")

    try:
        init_db()
        if not is_prod_env():
            add_defaults_feed()

    except:
        logging.error(f"Failed to initialize database: {os.getenv('POSTGRES_HOST')}", exc_info=True)
        exit(1)

    # Init APP
    feed_to_crawl = Queue()
    scheduler_init(feed_to_crawl)

    crawler(feed_to_crawl)
    Thread(target=crawler, args=(feed_to_crawl,)).start()

    while True:
        schedule.run_pending()
        sleep(1)
