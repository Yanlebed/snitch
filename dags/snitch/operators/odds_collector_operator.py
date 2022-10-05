from airflow.operators.python_operator import PythonOperator
from scrapy.crawler import CrawlerProcess

from snitch.main import DEFAULT_HEADERS
from snitch.scrapers.odds_collector import OddsCollector


class OddsCollectorOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "odds_collector_task"
        super(OddsCollectorOperator, self).__init__(
            python_callable=self.retrieve_odds,
            *args,
            **kwargs)

    @staticmethod
    def retrieve_odds():
        process = CrawlerProcess(DEFAULT_HEADERS)
        process.crawl(OddsCollector)
        process.start()
