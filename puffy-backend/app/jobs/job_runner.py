import logging
import time
from typing_extensions import Annotated
from fastapi import Depends

from app.db import OrderRepoDep, PaymentRepoDep, get_db
from app.jobs.payment_crawler import PaymentCrawler, PaymentCrawlerDep


logger = logging.getLogger(__name__)


def run_payment_crawler_job():
    """Main job runner that runs payment crawler every minute"""

    while True:
        try:
            logger.info("Starting payment crawler job")

            # Get database session and repositories
            db = get_db().__enter__()
            order_repo = db
            payment_repo = db

            # Get payment crawler instance
            crawler = PaymentCrawler(order_repo, payment_repo)

            # Run crawler
            crawler.crawl_payments()

            logger.info("Payment crawler job completed")

        except Exception as err:
            logger.error(f"Payment crawler job failed: {err}")

        finally:
            if 'db' in locals():
                db.close()

        # Sleep for 1 minute
        logger.info("Waiting 1 minute before next crawl...")
        time.sleep(60)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_payment_crawler_job()
