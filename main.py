from flask import Flask, render_template
from datetime import datetime
import pickle
from get_data import api_data


USE_CACHE = True


app = Flask(__name__)

def get_cached_data(filename):
  t, data = pickle.load( open( filename, "rb" ) )
  diff = t - datetime.now()
  diff_sec = diff.seconds + diff.days * 86400
  sec_hour = 60 * 60
  if diff_sec < sec_hour:
    return data
  return None


def cache_data(filename, data):
  pickle.dump((datetime.now(), data) , open( filename, "wb" ) )

@app.route('/')
def index():
    data = []

    filename = 'cache.pkl'

    if USE_CACHE:
      data = get_cached_data(filename)
    else:
      data = None
      
    if data is None:
      data = api_data()
      cache_data(filename, data)


    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(data)

    # print(data)

    return render_template('index.html', properties=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    app.run(debug=True, use_reloader=True)
