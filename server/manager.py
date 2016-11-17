from server import app

port_list = [3000, 3001, 3002, 3003, 3004]
worker_list = []


@app.route('/worker/<port>', methods=["GET"])
def append(port):
    if int(port) in port_list:
        worker_list.append(port)
        return 'ok'


def get_worker():
    if len(worker_list) > 0:
        now = worker_list[0]
        worker_list.pop(0)
        worker_list.append(now)
        return now
    else:
        return -1