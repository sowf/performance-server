import redis
import logging
import logging.config
from datetime import datetime
from flask import Flask
from flask_restful import Resource, Api, reqparse
from settings import REDIS_HOST, REDIS_PORT, LOGGING_CONF
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
    def get(self):
        logger.info(f"GET {self.__class__}")

        dt_now = datetime.now().strftime("%m:%d:%H:%M:%S")
        redis.hset(dt_now, "method", "GET")

        res = {
            'data': {
                'cpu': get_cpu(),
                'ram': get_ram(),
                'gpu': get_gpu()
            }
        }
        return res

    def post(self):
        logger.info(f"POST {self.__class__}")

        args = parser.parse_args()

        dt_now = datetime.now().strftime("%m:%d:%H:%M:%S")
        redis.hset(dt_now, "method", "POST")
        redis.hset(dt_now, "type", args.get('type'))

        if args.get('type') == 'cpu':
            res = {'data': {'cpu': get_cpu()}}
        elif args.get('type') == 'ram':
            res = {'data': {'ram': get_ram()}}
        elif args.get('type') == 'gpu':
            res = {'data': {'gpu': get_gpu()}}
        else:
            res = {'error': "Wrong performance type."}, 404

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
            res = {'error': "Неизвестная ошибка."}, 500

        return res


api.add_resource(Performance, '/api/performance/')
api.add_resource(Manager, '/api/manager/')


if __name__ == '__main__':
    app.run(debug=True)
