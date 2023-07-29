import json
from database.model import MusicChart
from database.db_config import db_session
from sqlalchemy.exc import IntegrityError

json_file_path = 'charts.json'

with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)

for chart_data in json_data:
    del chart_data['chart_publication_date']
    chart = MusicChart(**chart_data)
    chart.source_recognised = True
    db_session.add(chart)
    try:
        db_session.commit()
    except IntegrityError:
        print(f'Unique Violation for {chart_data}')
        db_session.rollback()
        continue
db_session.close()
