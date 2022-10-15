import telebot

from datetime import datetime, timedelta
from os.path import abspath, dirname

from airflow import DAG
from snitch.operators.match_collector_operator import MatchCollectorOperator
from snitch.operators.details_collector_operator import DetailsCollectorOperator
from snitch.operators.odds_collector_operator import OddsCollectorOperator
from snitch.operators.telegram_post_operator import TelegramPostOperator
from snitch.operators.expected_counter_operator import ExpectedCounterOperator
from snitch.operators.sheet_editor_operator import SheetEditorOperator
from snitch.operators.in_live_operator import InLiveOperator


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
dag = DAG('match_assembler', schedule_interval='50 21 * * *', default_args=default_args, max_active_runs=1,
          orientation='LR')
match_collector_task = MatchCollectorOperator(dag=dag, task_id='match_collector_task')
odds_collector_task = OddsCollectorOperator(dag=dag, task_id='odds_collector_task')
telegram_post_task = TelegramPostOperator(dag=dag, task_id='telegram_post_task',
                                          op_kwargs={'bot': bot, 'chat_id': bot_chat_id})
expected_goals_counter_task = ExpectedCounterOperator(dag=dag, task_id='expected_goals_counter_task')
sheet_editor_task = SheetEditorOperator(dag=dag, task_id='sheet_editor_task')

odds_collector_task.set_upstream(match_collector_task)
expected_goals_counter_task.set_upstream(odds_collector_task)
telegram_post_task.set_upstream(expected_goals_counter_task)
sheet_editor_task.set_upstream(telegram_post_task)


in_live_dag = DAG('in_live', default_args=default_args, max_active_runs=1, orientation='LR')
in_live_task = InLiveOperator(dag=in_live_dag, task_id='in_live_task')
new_sheet_editor_task = SheetEditorOperator(dag=in_live_dag, task_id='sheet_editor_task')
new_sheet_editor_task.set_upstream(in_live_task)


globals()['match_assembler'] = dag
globals()['in_live'] = dag
