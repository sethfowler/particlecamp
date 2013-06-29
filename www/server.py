#!/usr/bin/env python

import json

from flask import Flask
from flask import render_template
app = Flask(__name__)

# Some fake data. Eventually this will come from CSV.
data = [
    [10, 10, 5 ],
    [12, 15, 6 ],
    [14, 13, 11],
    [11, 9,  10],
    [8,  5,  3 ],
  ]

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/data')
def ajax_data():
    return json.dumps(data)

if __name__ == '__main__':
    app.run(debug=True)
