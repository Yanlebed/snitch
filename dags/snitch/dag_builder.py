import logging
import telebot

from datetime import datetime, timedelta
from os.path import abspath, dirname

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from scrapy.crawler import CrawlerProcess
from snitch.main import DEFAULT_HEADERS
from snitch.scrapers.match_collector import MatchCollector
from snitch.scrapers.details_collector import DetailsCollector
from snitch.scrapers.odds_collector import OddsCollector
from snitch.operators import MatchCollectorOperator, DetailsCollectorOperator, OddsCollectorOperator, \
    TelegramPostOperator, SheetEditorOperator

bot_token = '5775727156:AAFji3qtTLvO4ZmFIOsLuAEsDCeM30XT7dw'
bot_chat_id = 354467348
bot = telebot.TeleBot(bot_token)

dags_dir = dirname(abspath(__file__))

first_start = datetime.combine(datetime.today() - timedelta(1), datetime.min.time())  # 02:00 AM today
default_args = {
    'owner': 'bookly',
    'depends_on_past': False,
    'start_date': first_start,
    'email': ['bookly.beekly@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}
dag = DAG('match_assembler', schedule_interval='05 0 * * *', default_args=default_args, max_active_runs=1,
          orientation='LR')
match_collector_task = MatchCollectorOperator(dag=dag, task_id='match_collector_task')
odds_collector_task = OddsCollectorOperator(dag=dag, task_id='odds_collector_task')
telegram_post_task = TelegramPostOperator(dag=dag, task_id='telegram_post_task',
                                          op_kwargs={'bot': bot, 'chat_id': bot_chat_id})
sheet_editor_task = SheetEditorOperator(dag=dag, task_id='sheet_editor_task')

odds_collector_task.set_upstream(match_collector_task)
telegram_post_task.set_upstream(odds_collector_task)
sheet_editor_task.set_upstream(telegram_post_task)

globals()['match_collector'] = dag
