from flask import Flask
from flask import render_template

from datetime import datetime
import json
import os
import psycopg2 as dbapi2
from random import randrange
import re


app = Flask(__name__)


@app.route('/')
def home():
    now = datetime.now()
    return render_template('home.html', current_time=now.ctime())


@app.route('/random')
def random_numbers():
    with dbapi2.connect(app.config['db_params']) as db:
        with db.cursor() as cursor:
            query = "CREATE TABLE IF NOT EXISTS dummy (num INTEGER PRIMARY KEY)"
            cursor.execute(query)
            query = "INSERT INTO dummy (num) VALUES (%s)"
            num = randrange(200)
            cursor.execute(query, (num,))
            db.commit()

            query = "SELECT num FROM dummy"
            cursor.execute(query)
            nums = [r[0] for r in cursor.fetchall()]
    return "Stored numbers: %s" % ', '.join(map(str, nums))


def get_db_params():
    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        parsed = json.loads(VCAP_SERVICES)
        uri = parsed["elephantsql"][0]["credentials"]["uri"]
        match = re.match('postgres://(.*?):(.*?)@(.*?):5432/(.*)', uri)
        user, password, host, dbname = match.groups()
    else:
        user, password, host, dbname = 'vagrant', 'vagrant', 'localhost', 'itucsdb'
    return "user='{}' password='{}' host='{}' dbname='{}'".format(user, password, host, dbname)


if __name__ == '__main__':
    app.config['db_params'] = get_db_params()
    PORT = int(os.getenv('VCAP_APP_PORT', '5000'))
    app.run(host='0.0.0.0', port=int(PORT))