# from server import app
from pywebhdfs.webhdfs import PyWebHdfsClient

# @app.route('/hdfs', methods=["GET", "POST"])
# def hdfs():
# 	# default line
# 	hdfs = PyWebHdfsClient(host='localhost',port='5000', user_name='hdfs')
# 	my_file = "/Users/inkg/Downloads/soma/s_s/soan/server/uploads/1/origin/files/testerp/LoginActivity.java"
# 	hdfs.read_file(my_file)

# if __name__ == '__main__':
#     app.run(debug=True, port=4444, host='0.0.0.0')

if __name__ == '__main__':
	
	hdfs = PyWebHdfsClient(host='localhost',port='50070', user_name='inkg')
	my_data = "hahaha"
	my_file = "user/LoginActivity.java"
	# my_file = "user/NewActivity.java"
	# print hdfs.create_file(my_file, my_data)
	print hdfs.read_file(my_file)