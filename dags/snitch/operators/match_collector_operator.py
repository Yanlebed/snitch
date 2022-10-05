from airflow.operators.python_operator import PythonOperator
from scrapy.crawler import CrawlerProcess

from snitch.main import DEFAULT_HEADERS
from snitch.scrapers.match_collector import MatchCollector


class MatchCollectorOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "match_collector_task"
        super(MatchCollectorOperator, self).__init__(
            python_callable=self.run_collector,
            *args,
            **kwargs)

    @staticmethod
    def run_collector():
        process = CrawlerProcess(DEFAULT_HEADERS)
        process.crawl(MatchCollector)
        process.start()
