"""
Даг для экстракции данных NHL
"""

from datetime import datetime
from airflow import DAG
from typing import Dict, Optional, Tuple, Union
from airflow.operators.python_operator import PythonOperator
import clickhouse_connect
from modules.nhl_miner import NHLMiner
from airflow.hooks.base import BaseHook

miner = NHLMiner()

def _mapp_team_stats(raw_item: Dict, ts: str):
    
    stat_type = raw_item['type']
    game_type = stat_type.get('gameType', {})
    team = raw_item['splits'][0]['team']
    stat = raw_item['splits'][0].get('stat', {})

    result = {
        'requested_at': datetime.strptime(ts, '%Y%m%dT%H%M%S'),
        'team_id': team['id'],
        'team_name': team['name'],
        'stat_name': stat_type.get('displayName'),
        'game_type_id': game_type.get('id') if game_type else '',
        'game_type_description': game_type.get('description') if game_type else '',
        'statistics': f'{stat}'
    }

    return result



def _extract_team_stats( **kwargs):
    teams = ['21', '22', '23']
    load_data=[]
    for team_id in teams:
        print(f'Collecting data for tema_id={team_id}...')
        extract_data = miner.get_data(query_type='team_stats', team_id=team_id )

        if extract_data.get('stats'):
            for item in extract_data['stats']:
                mapped_item = _mapp_team_stats(item, kwargs['ts_nodash'])
                load_data.append(mapped_item)
        else:
            print(f'API warning: no stats for team_id={team_id}')
    
    credentials = BaseHook.get_connection(kwargs['hook_id']) 
    ch_client = clickhouse_connect.get_client(host=str(credentials.host), 
                                              username=str(credentials.login), 
                                              password=str(credentials.password),
                                              database='staging'
                                              )

    load_data_flat = [list(x.values()) for x in load_data]
    column_names = list(load_data[0].keys())

    ch_client.insert('nhl_team_stats', load_data_flat, column_names=column_names) 

    print("Insertion is done.")


dag = DAG(
    dag_id="assemble_actual_campaign_stats",
    max_active_runs=1,
    default_args={
        "owner": "ens-a",
        "start_date": datetime(2023, 3, 10),
    },
    schedule_interval='0 */12 * * *',
    catchup=False
)


extract_team_stats = PythonOperator(
    task_id='extract_team_stats',
    provide_context=True,
    python_callable=_extract_team_stats,
    op_kwargs={
        'hook_id': 'local_clickhouse'
    },
    dag=dag
)


extract_team_stats
