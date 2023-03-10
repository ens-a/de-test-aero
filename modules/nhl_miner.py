import requests
from typing import Dict, Optional, Tuple, Union
# from airflow import AirflowException

'''
Класс для работы API NHL v1
'''

class NHLMiner():

    def get_data(self, query_type: str, team_id: str, query_parameters: Optional[Dict]=None) -> Dict:
        '''
        Функция для получения данных из API NHL
        :param team_id: идентификатор команды
        :param query_parameters: параметры запроса
        :param query_type: тип запроса
        :return: ответ от API в формате json
        '''

        if query_type == 'team_stats':
            result = self.process_request(team_id, query_parameters)
        else:
            pass
            # raise AirflowException(f"Unknown query_type {query_type}")

        return result

    def process_request(self, team_id: str, data: Dict) -> Dict:
        url = f'https://statsapi.web.nhl.com/api/v1/teams/{team_id}/stats'  
        print(f'Sending request on url: {url}')

        result_data, resp_status, resp_headers = self.make_request(
            url=url,
            method='get',
            params=data,
            headers={
                'Content-Type': 'application/json'
            }
        )

        if not result_data:
                return {}

        if resp_status != 200:
            # TODO Нужно заменить на внятную ошибку с выводом детализации ошибки
            # raise AirflowException('API malfunction:')
            pass
        return result_data

    def make_request(self, url: str, params: Optional[Dict]=None, headers: Optional[Dict]=None,
                            auth: Tuple[str, str]=None, method: Optional[str]='get', **kwargs) -> Tuple[Union[Dict, str], int, Dict]:
        params = params or {}
        headers = headers or {}
        result_data, resp_status, resp_headers = None, None, None

        try:
            if method == 'post':
                response = requests.post(url, data=params, headers=headers, auth=auth, **kwargs)
            else:
                response = requests.get(url, params=params, headers=headers, auth=auth, **kwargs)

            resp_status = response.status_code
            resp_headers = response.headers

            try:
                result_data = response.json()
            except Exception as e:
                result_data = response.text
        except Exception as e:
            raise Exception(f'Malfunction during execution of "{method}" call: {e}')

        return result_data, resp_status, resp_headers
