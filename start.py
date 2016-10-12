# -*- coding: utf-8 -*-
from server import app
from server import db

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=5000, host='0.0.0.0')