from server import app

port_list = [3000, 3001, 3002, 3003, 3004]
worker_list = []


@app.route('/worker/<port>', methods=["GET"])
def append(port):
    print 'add : ' + str(port)
    worker_list.append(port)
    return 'ok'


def get_worker():
    if len(worker_list) > 0:
        now = worker_list[0]
        print 'now worker : ' + str(now)
        worker_list.pop(0)
        worker_list.append(now)
        return now
    else:
        return -1
'''
def is_alive(worker):
    if worker in port_list:
        url = 'http://0.0.0.0:' + str(worker) + '/alive'
        print 'check ' + url
        res = urllib2.urlopen(url)
        #res = requests.get(url, timeout=3)
        #if res.status_code < 400:
        if res.code < 400:
            print str(worker) + ' is alive'
            return True
        else:
            print str(worker) + ' is dead'
            return False


def init_worker():
    print 'init worker'
    for i in port_list:
        if is_alive(int(i)):
            worker_list.append(int(i))
            print 'add ' + str(i)
        else:
            print str(i) + ' is not alive'
'''