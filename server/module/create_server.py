import collections
import ast
from passer import db
from passer.models import Server
from sqlalchemy import inspect
from sqlalchemy.orm import mapper

class Server_api():
    def __init__(self):
        self.engine = db.engine
        self.metadata = db.MetaData(self.engine)
        self.metadata.reflect()
        self.inspector = inspect(db.engine)

    def _unique_ip_check(self):
        tables = [x for x in self.inspector.get_table_names() if x.find('pr_') != -1]
        ip_list = []
        for table in tables:
            columns = db.session.query(self.metadata.tables[table]).all()
            for data in columns:
		ip_list.append(data.s_ip)
                check = [item for item, count in collections.Counter(ip_list).items() if count > 1]
        if len(check) != 0:
            _ret = '{"dup_ip": ['
            for data in check:
                _ret += '"' + data + '"' + ', '
            _ret += '] }'
            return ast.literal_eval(_ret)
        else:
            return True


def create_server_group(server_group):
    if server_group in 'pr_':
        pass
    else:
        server_group = 'pr_' + server_group
    engine = db.engine
    metadata = db.MetaData()
    inspector = inspect(engine)
    server_tables = db.Table(server_group, metadata,
        db.Column('idx', db.Integer, primary_key=True, autoincrement=True),
        db.Column('number', db.Integer, nullable=False, default=0),
        db.Column('team', db.String(50), nullable=False),
        db.Column('s_name', db.String(50), nullable=False, unique=True),
        db.Column('s_ip', db.String(50), nullable=False, unique=True),
        db.Column('s_type', db.String(20), nullable=False),
        db.Column('port', db.Integer, nullable=False),
        db.Column('password', db.String(255), nullable=False),
        db.Column('accounts', db.String(1000), nullable=False)
    )
    if server_group in inspector.get_table_names():
        return server_tables
    metadata.create_all(engine)
    return True


if __name__ == '__main__':
    print create_server_group('test')
