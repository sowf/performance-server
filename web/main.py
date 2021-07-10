import redis
import logging
import logging.config
from datetime import datetime
from flask import Flask
from flask_restful import Resource, Api, reqparse
from settings import (
    REDIS_HOST,
    REDIS_PORT,
    LOGGING_CONF,
    FLASK_DEBUG,
    FLASK_PORT
)
from services import filter_keys, get_cpu, get_ram, get_gpu


logging.config.dictConfig(LOGGING_CONF)
logger = logging.getLogger(__name__)


redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT
)


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('type')
parser.add_argument('from')
parser.add_argument('to')


class Performance(Resource):
    def set_data(self, dt_now, data):
        for key, value in data.items():
            if value:
                redis.hset(dt_now, key, value)

        return data

    def get(self):
        logger.info(f"GET {self.__class__}")

        dt_now = datetime.now().strftime("%m:%d:%H:%M:%S")
        redis.hset(dt_now, "method", "GET")

        data = {
            'cpu': get_cpu(),
            'ram': get_ram(),
            'gpu': get_gpu()
        }

        return {"data": self.set_data(dt_now, data)}

    def post(self):
        logger.info(f"POST {self.__class__}")

        args = parser.parse_args()

        dt_now = datetime.now().strftime("%m:%d:%H:%M:%S")
        redis.hset(dt_now, "method", "POST")

        data = {}

        if args.get('type') == 'cpu':
            data['cpu'] = get_cpu()
        elif args.get('type') == 'ram':
            data['ram'] = get_ram()
        elif args.get('type') == 'gpu':
            data['gpu'] = get_gpu()

        res = {}, 404
        if data:
            res = {"data": self.set_data(dt_now, data)}

        return res


class Manager(Resource):
    def get(self):
        logger.info(f"GET {self.__class__}")

        data = dict()

        keys = redis.keys('*')
        for key in keys:
            # bytes -> string
            str_key = key.decode()
            values = redis.hgetall(str_key)
            new_values = {
                key.decode(): val.decode() for key, val in values.items()
            }

            data[str_key] = new_values

        res = {'data': data}

        return res

    def post(self):
        logger.info(f"POST {self.__class__}")

        args = parser.parse_args()

        res = {}, 204

        try:
            keys = redis.keys('*')
            filtered_keys = filter_keys(
                keys,
                args.get('from', ''),
                args.get('to', '')
            )

            for key in filtered_keys:
                redis.delete(key)

        except Exception as e:
            logger.error(e, exc_info=True)
            res = {}, 500

        return res


api.add_resource(Performance, '/api/performance/')
api.add_resource(Manager, '/api/manager/')


if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT)
