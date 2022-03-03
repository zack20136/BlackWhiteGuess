from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import ssl
import threading
import time

# 全域變數
SERVER_CERT = './Openssl/server.cer'
SERVER_KEY = './Openssl/server.key'

lock = threading.Lock()

IP = '0.0.0.0'
PORT = 3000

room = []

class room_data():
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2
		self.d1 = 0
		self.d2 = 0
		self.r1 = ''
		self.r2 = ''

class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
	pass

def data_init():
	name = []
	account = []
	password = []
	with open('player.txt') as f:
		for line in f.readlines():
			s = line.split(', ')
			name.append(s[0])
			account.append(s[1])
			password.append(s[2])
	with open('player.txt', 'w') as f:
		f.write('name, account, password, key\n')
		for i in range(1, len(name)):
			f.write(name[i] + ', ' + account[i] + ', ' + password[i] + ', ' + '0' + '\n')
	return 0

# 讀取使用者資料
def load_player_data():
	name = []
	account = []
	password = []
	key = []
	with open('player.txt') as f:
		for line in f.readlines():
			s = line.split(', ')
			name.append(s[0])
			account.append(s[1])
			password.append(s[2])
			s = s[3].split('\n')
			key.append(s[0])
	return name, account, password, key

# 遊戲
class Game:
	def register(self, p_name, p_account, p_password): # 註冊
		if len(p_name) < 3:
			return '名稱至少三個字'
		if (len(p_account) < 1) | (len(p_password) < 1):
			return '帳號密碼不能空白'
		result = load_player_data()
		name = result[0]
		account = result[1]
		with open('player.txt', 'a') as f:
			if p_name in name:
				return '此名稱已被使用'
			elif p_account in account:
				return '此帳號已被使用'
			else:
				lock.acquire()
				f.write(p_name + ', ' + p_account + ', ' + p_password + ', ' + '0' + '\n')
				lock.release()
				print('玩家 ' + p_name + ' 註冊成功')
				return '註冊成功'

	def login(self, p_account, p_password): # 登入
		if (len(p_account) < 1) | (len(p_password) < 1):
			return '帳號密碼不能空白'
		result = load_player_data()
		name = result[0]
		account = result[1]
		password = result[2]
		key = result[3]
		online = 0
		for i in range(1, len(name)):
			if key[i] != '0':
				online += 1
		if online>40:
			return '伺服器滿載'
		for i in range(1, len(name)):
			if (p_account == account[i]) & (p_password == password[i]):
				if key[i] == '0':
					p_name = name[i]
					key[i] = '1'
					lock.acquire()
					with open('player.txt', 'w') as f:
						for j in range(0, len(name)):
							f.write(name[j] + ', ' + account[j] + ', ' + password[j] + ', ' + key[j] + '\n')
					lock.release()
					print('玩家 ' + p_name + ' 登入')
					return '登入成功', p_name
				return '此帳號已被登入'
		return '帳號密碼錯誤'

	def logout(self, p_name): # 登出
		result = load_player_data()
		name = result[0]
		account = result[1]
		password = result[2]
		key = result[3]
		i = 0
		while p_name != name[i]:
			i += 1
		key[i] = '0'
		lock.acquire()
		with open('player.txt', 'w') as f:
			for j in range(0, len(name)):
				f.write(name[j] + ', ' + account[j] + ', ' + password[j] + ', ' + key[j] + '\n')
		lock.release()
		print('玩家 ' + p_name + ' 登出')
		return '登出成功'

	def hall(self): # 大廳
		result = load_player_data()
		name = result[0]
		key = result[3]
		player = []
		state = []
		for i in range(1, len(name)):
			if key[i] != '0':
				player.append(name[i])
				state.append(key[i])
		return player, state

	def target(self, p_name, target_name): # 標記
		result = load_player_data()
		name = result[0]
		account = result[1]
		password = result[2]
		key = result[3]
		for i in range(1, len(name)):
			if name[i] == target_name:
				if key[i] == '1':
					key[i] = p_name
					break
				return '玩家忙碌中'
		lock.acquire()
		with open('player.txt', 'w') as f:
			for i in range(0, len(name)):
				f.write(name[i] + ', ' + account[i] + ', ' + password[i] + ', ' + key[i] + '\n')
		lock.release()
		return '成功標記'

	def distarget(self, p_name, cmd='1'): # 取消標記
		result = load_player_data()
		name = result[0]
		account = result[1]
		password = result[2]
		key = result[3]
		for i in range(1, len(name)):
			if name[i] == p_name:
				if (key[i] != '0') & (key[i] != '1'):
					key[i] = cmd
					break
				return '沒有被標記'
		lock.acquire()
		with open('player.txt', 'w') as f:
			for i in range(0, len(name)):
				f.write(name[i] + ', ' + account[i] + ', ' + password[i] + ', ' + key[i] + '\n')
		lock.release()
		return '成功取消標記'

	def createroom(self, p1, p2): # 創建房間
		room.append(room_data(p1, p2))
		print('玩家 ' + p2 + '創建房間')
		return 0

	def delroom(self, num): # 刪除房間
		del room[num]
		print('刪除房間 ' + str(num))
		return 0

	def getroomnum(self, p_name): # 獲取房號
		while True:
			for i in range(0, len(room)):
				if p_name == room[i].p1:
					return i
				elif p_name == room[i].p2:
					return i
			time.sleep(0.1)

	def mora(self, room_num, p_name, cmd): # 猜拳
		if p_name == room[room_num].p1:
			room[room_num].d1 = cmd
		else:
			room[room_num].d2 = cmd
		while (room[room_num].d1==0) | (room[room_num].d2==0):
			time.sleep(0.1)
		if room[room_num].d1 == room[room_num].d2:
			room[room_num].r1 = 'TIE'
		elif ((room[room_num].d1 == 2)&(room[room_num].d2 == 1)) | ((room[room_num].d1 == 3)&(room[room_num].d2 == 2)) | ((room[room_num].d1 == 1)&(room[room_num].d2 == 3)):
			room[room_num].r1 = room[room_num].p1
		elif ((room[room_num].d2 == 2)&(room[room_num].d1 == 1)) | ((room[room_num].d2 == 3)&(room[room_num].d1 == 2)) | ((room[room_num].d2 == 1)&(room[room_num].d1 == 3)):
			room[room_num].r1 = room[room_num].p2
		d1 = room[room_num].d1
		d2 = room[room_num].d2
		time.sleep(0.5)
		room[room_num].d1 = 0
		room[room_num].d2 = 0
		if p_name == room[room_num].p1:
			return room[room_num].r1, d1, d2
		else:
			return room[room_num].r1, d2, d1

	def udlr(self, room_num, p_name, cmd): # 猜方向
		if p_name == room[room_num].p1:
			room[room_num].d1 = cmd
		else:
			room[room_num].d2 = cmd
		while (room[room_num].d1==0) | (room[room_num].d2==0):
			time.sleep(0.1)
		if room[room_num].d1 == room[room_num].d2:
			room[room_num].r2 = room[room_num].r1
		else:
			room[room_num].r2 = 'AGAIN'
		d1 = room[room_num].d1
		d2 = room[room_num].d2
		time.sleep(0.5)
		room[room_num].d1 = 0
		room[room_num].d2 = 0
		if p_name == room[room_num].p1:
			return room[room_num].r2, d1, d2
		else:
			return room[room_num].r2, d2, d1
# end of Game

# SERVER資訊
def DataThread():
	while True:
		result = Game.hall(0)
		print('############################################')
		print('在線玩家: ' + str(len(result[0])))
		for i in range(0, len(result[0])):
			print('  玩家: ' + result[0][i] + '   狀態: ' + result[1][i])
		print('房間數量: ' + str(len(room)))
		for i in range(0, len(room)):
			print('  房間 ' + str(i+1) + ': ' + room[i].p1 + ' VS ' + room[i].p2)
		print('############################################')
		time.sleep(3)
# end of DataThread

def main():
	# connect
	server = ThreadXMLRPCServer((IP, PORT)) # 註冊SERVER
	server.register_instance(Game())

	# SSL
	ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	ctx.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
	server.socket = ctx.wrap_socket(server.socket, server_side=True)

	# init
	data_init()
	info = threading.Thread(target=DataThread)
	info.start()

	# main
	try:
		print('Use Control-C to exit!')
		server.serve_forever()
	except KeyboardInterrupt:
		print('Server exit')
	except Exception as e:
		print('Other exception: %s' % str(e))
# end of main

if __name__ == '__main__':
	main()
