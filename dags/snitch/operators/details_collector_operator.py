from airflow.operators.python_operator import PythonOperator

from snitch.scrapers.details_collector import DetailsCollector


class DetailsCollectorOperator(PythonOperator):

    def __init__(self,
                 *args,
                 **kwargs):
        self.task = "details_collector_task"
        super(DetailsCollectorOperator, self).__init__(
            python_callable=self.run_collector,
            *args,
            **kwargs)

    @staticmethod
    def run_collector():
        details = DetailsCollector(match_id=None)
        details.parse()
