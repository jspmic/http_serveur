import time
from socket import *
from json import load

#Old

class Server:

	# Main Server Class

	def __init__(self,host:str='localhost',port:int=9000):
		self.HOST = host
		self.PORT = port
		self.server = socket(AF_INET,SOCK_STREAM)
		self.server.bind((self.HOST,self.PORT))
		self.server.listen(5)
		self.mimes = load(open('mimes.json')) #loading all MIME from the json file
		self.status = 'none' #attribute to signal the state of the request&response

	def response_maker(self,request):

		''' Example: request = GET /file.ext HTTP/1.1\n ... + headers 
		request -> response( HTTP/1.1 200 OK ... + file )
					or
		request -> response (HTTP/1.1 404 Not Found ... + html'''

		try:
			#Splitting according to new lines to extract the GET request
			self.get= request.split('\n')[0]

			#Splitting according to spaces to get the filename only
			self.file = self.get.split()[1]

			#Trying to find the corresponding MIME to the requested file extension
			if self.file=='/':
				self.file = 'index.html'
				f_content =  open(self.file,'rb').read()
				self.mime = 'text/html'
			else:
				self.file = self.file.replace('/','')
				ext = self.file[self.file.find('.'):]
				self.mime = self.mimes.get(ext,'not/found')
				f_content = open(self.file,'rb').read()

			#Assembling some headers together
			headers = f"""{self.get.split()[2]} 200 OK\r
			Content-Type: {self.mime}; charset=utf-8\r
			Content-Length: {len(f_content)}\r
			Date: {time.strftime('%a, %d %b %Y %I:%M:%S %Z',time.gmtime())}\r\n\r\n""".replace('\t','')

			#Constructing the final response
			self.response = headers.encode()+f_content+b"\r\n\r\n"

			#Setting status to okay, for the program to be alerted everything went good
			self.status = 'okay'
			print("file sent")

		except Exception as e:

			#Assembling an error response
			self.response = f"""{self.get.split()[2]} 404 Not Found\r
			Content-Type:text/html; charset:utf-8\r
			Date: {time.strftime('%a, %d %b %Y %I:%M:%S %Z',time.gmtime())}\r
			Content-Length: 156\r\n\r
			<html>
				<head>
					<title>404 Not Found</title>
				</head>
					<body>
						<h1 style="color:red;">404 File not found</h1>
					</body>
			</html>\r\n\r\n""".replace('\t','').encode()

			#Setting status to bad, for the program to know we encountered some errors
			self.status = 'bad'

			#Error viewer(for debugging)
			print(f"Error encountered: {e}")
			print("File not found!\nSent 404 code")

		finally:
			print(f"Status: {self.status}\n--------\n")

	def __str__(self):
		return f"Listening on {self.HOST}:{self.PORT}\n"
	def __repr__(self):
		return f"Listening on {self.HOST}:{self.PORT}\nOnly 5 users are allowed to wait\n"

def client_handler(obj):
		while True:

			#Allowing client to connect on our server
			obj.client,address = obj.server.accept()

			#Receiving the first client's request
			request = obj.client.recv(1024).decode()
			obj.response_maker(request)
			local = time.strftime("[%a %d.%m.%y (%H:%M:%S)]",time.localtime())
			print(f"{address[0]} {local} -- {obj.get}")
			obj.client.send(obj.response)

			#Verifying if there is no 404
			if obj.status=='bad': obj.client.shutdown(SHUT_WR)

if __name__=='__main__':
	host = input("Host: ")
	port = int(input("Port: "))
	server = Server(host,port)
	print(server)
	client_handler(server)
