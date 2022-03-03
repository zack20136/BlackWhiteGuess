import xmlrpc.client
import ssl
import threading
import tkinter as tk
import tkinter.messagebox
import random
import time

# 全域變數
IP = '127.0.0.1'
PORT = 3000

hall_run = False
mora_whowin = ''
 # 遊戲訊息
gametext = ''
p1_c = ''
p2_c = ''
mora = {1:'剪刀', 2:'石頭', 3:'布'}
udlr = {1:'上', 2:'下', 3:'左', 4:'右'}

img = [] # 圖檔

p_num = 0 # 玩家數量
p_pos = [] # 玩家位置陣列
p_now = [] #  出現在大廳玩家

p_name = '' # 玩家名稱
p2_name = '' # 對手名稱
room_num = -1 # 房號

class p_data(): # 玩家位置資料
	def __init__(self, name='', i=0, j=0):
		self.name = name
		self.i = i
		self.j = j

def center_window(root, width, height): # 視窗置中
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()

	x = (screen_width/2) - (width/2)
	y = (screen_height/2) - (height/2)
	root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def main():
	# 連線
	server = xmlrpc.client.ServerProxy('https://' + IP + ':' + str(PORT), context = ssl.SSLContext())

	print('Connecting to %s port %s' % (IP, PORT))

	# main
	try:
		def window_close(): # 關閉視窗
			if tkinter.messagebox.askokcancel(title='退出', message='是否要退出'):
				global p_name, hall_run
				if p_name != '':
					result = server.logout(p_name)
					p_name = ''
					print(result)
				hall_run = False
				window.destroy()
				print('退出')
		
		def usr_sign_up(): # 註冊頁面
			def register(): # 註冊
				name = var_usr_name.get()
				account = var_usr_account.get()
				password = var_usr_pwd.get()
				result = server.register(name, account, password)
				if result != '註冊成功':
					tkinter.messagebox.showerror(title='註冊', message=result)
				else:
					tkinter.messagebox.showinfo(title='註冊', message=result)
					window_sign_up.destroy()

			# 視窗
			window_sign_up = tk.Toplevel(window)
			window_sign_up.title('註冊')
			center_window(window_sign_up, 400, 300)
			window_sign_up.resizable(width=0, height=0)

			tk.Label(window_sign_up, text='註冊', font=("",40)).place(x=150, y=20)

			tk.Label(window_sign_up, text='名稱：', font=("",12)).place(x=100, y=110)
			var_usr_name=tk.StringVar()
			entry_usr_name=tk.Entry(window_sign_up, textvariable=var_usr_name)
			entry_usr_name.place(x = 155, y = 110)

			tk.Label(window_sign_up, text='帳號：', font=("",12)).place(x=100, y=140)
			var_usr_account = tk.StringVar()
			entry_usr_account = tk.Entry(window_sign_up, textvariable=var_usr_account)
			entry_usr_account.place(x=155, y=140)

			tk.Label(window_sign_up, text='密碼：', font=("",12)).place(x=100, y=170)
			var_usr_pwd = tk.StringVar()
			entry_usr_pwd = tk.Entry(window_sign_up, textvariable=var_usr_pwd,show='*')
			entry_usr_pwd.place(x=155, y=170)

			btn_comfirm_sign_up = tk.Button(window_sign_up, text=' 確定 ', command=register, font=("",12))
			btn_comfirm_sign_up.place(x=170, y=220)

		def usr_log_in(): # 登入頁面
			def login(): # 登入
				account = var_usr_account.get()
				password = var_usr_pwd.get()
				result = server.login(account, password)
				if result[0] != '登入成功':
					tkinter.messagebox.showerror(title='登入', message=result)
				else:
					global p_name
					p_name = str(result[1])
					tkinter.messagebox.showinfo(title='登入', message=result)
					window_login.destroy()
					window.switch_frame(hallface) # 跳轉到大廳頁面

			window_login = tk.Toplevel(window)
			window_login.title('登入')
			center_window(window_login, 400, 300)
			window_login.resizable(width=0, height=0)

			tk.Label(window_login, text='登入', font=("",40)).place(x=150, y=40)

			tk.Label(window_login, text='帳號：', font=("",12)).place(x=100, y=130)
			var_usr_account = tk.StringVar()
			entry_usr_account = tk.Entry(window_login, textvariable=var_usr_account)
			entry_usr_account.place(x=155, y=130)

			tk.Label(window_login, text='密碼：', font=("",12)).place(x=100, y=170)
			var_usr_pwd = tk.StringVar()
			entry_usr_pwd = tk.Entry(window_login, textvariable=var_usr_pwd,show='*')
			entry_usr_pwd.place(x=155, y=170)

			btn_comfirm_login = tk.Button(window_login, text=' 確定 ', command=login, font=("",12))
			btn_comfirm_login.place(x=170, y=220)

		def usr_log_out(): # 登出
			global p_name, hall_run
			if p_name != '':
				result = server.logout(p_name)
				p_name = ''
				tkinter.messagebox.showinfo(title='登出', message=result)
			window.switch_frame(initface) # 跳轉到初始頁面
			hall_run = False

		def target(target): # 標記
			result = server.target(p_name, target)
			if result != '成功標記':
				tkinter.messagebox.showerror(title='標記', message=result)
		
		def distarget(): # 取消標記
			result = server.distarget(p_name)
			if result != '成功取消標記':
				tkinter.messagebox.showerror(title='標記', message=result)

		class face(tk.Tk): # 介面跳轉控制
			def __init__(self):
				tk.Tk.__init__(self)
				self._frame = None
				self.switch_frame(initface)

			def switch_frame(self, frame_class):
				new_frame = frame_class(self)
				if self._frame is not None:
					self._frame.destroy()
				self._frame = new_frame
				self._frame.pack()

		class initface(tk.Frame): # 初始介面
			def __init__(self, root):
				tk.Frame.__init__(self, root, width=900, height=600)
				frame = tk.Frame(self, width=880, height=580, bg='#CDCD9A')
				frame.place(x=10, y=10)

				tk.Label(frame, text='黑白配', font=("",60), bg='#CDCD9A').place(x=330, y=60)
				bt_login = tk.Button(frame, text='  登 入  ', command=usr_log_in, font=("",20))
				bt_login.place(x=390, y=230)
				bt_sign = tk.Button(frame, text='  註 冊  ', command=usr_sign_up, font=("",20))
				bt_sign.place(x=390, y=300)
				bt_quit = tk.Button(frame, text='  退 出  ', command=window_close, font=("",20))
				bt_quit.place(x=390, y=370)

		class hallface(tk.Frame): # 大廳介面
			def __init__(self, root):
				tk.Frame.__init__(self, root, width=900, height=600)
				frame = tk.Frame(self, width=880, height=40, bg='#ADADAD')
				frame.place(x=12, y=10)
				tk.Label(frame, text='玩 家 ： '+p_name, font=("",12), bg='#ADADAD').place(x=60, y=10)
				self.online = tk.Label(frame, text='在線：'+str(p_num), font=("",12), bg='#ADADAD')
				self.online.place(x=800, y=10)
				tk.Label(frame, text='點擊玩家來發起對戰', font=("",12), bg='#ADADAD').place(x=350, y=10)
				bt_logout = tk.Button(frame, text='登出', command=usr_log_out, font=("",10))
				bt_logout.place(x=10, y=10)
				self.canvas = tk.Canvas(self, bg="#CDCD9A" , width=880, height=540)
				self.canvas.place(x=10, y=50)
				
				for i in range(0, 40):
					p_pos.append(p_data())
				
				self.canvas.bind('<Button-1>', hallface.click)

				info = threading.Thread(target=self.hall_update)
				info.start()
			
			def hall_update(self): # 更新大廳

				def create_player(root, name, state): # 新增玩家及圖示到大廳
					flag = 0
					for i in range(0,len(p_pos)):
						if name == p_pos[i].name:
							flag = i
					if flag == 0:
						i = random.randint(0,7)
						j = random.randint(0,4)
						n = i+j*8
						while p_pos[n].name != '':
							i = random.randint(0,7)
							j = random.randint(0,4)
							n = i+j*8
						x = i*100+60
						y = j*100+40
						p_pos[n].name = name
						p_pos[n].i = i
						p_pos[n].j = j
					else:
						x = (p_pos[flag].i)*100+60
						y = (p_pos[flag].j)*100+40
					root.create_oval(x, y, x+60, y+60, fill="white")
					root.create_text(x+30, y+30, text=name)
					if(state=='1'):
						root.create_text(x+30, y-10, text='空閒中')
					else:
						root.create_text(x+30, y-10, text='忙碌中')
					p_now.append(name)

				global hall_run, p_num, p2_name, p_now
				hall_run = True
				while hall_run:
					result = server.hall()
					p_num = len(result[0])
					self.online.config(text='在線：'+str(p_num))
					p_now = []
					flag = 0
					self.canvas.delete('all') 
					for i in range(0, p_num):
						if result[0][i] == p_name: # 判斷對戰是否成立
							if (result[1][i] != '1') & (result[1][i] != '2'):
								flag = 0
								for j in range(0, p_num):
									if (result[0][j] == result[1][i]) & (result[1][j] == p_name):
										tkinter.messagebox.showinfo(title='對戰', message='配對成功')
										p2_name = result[0][j]
										hall_run = False
										flag = 1
										break
								if flag == 0:
									if tkinter.messagebox.askyesno(title='對戰', message='是否接受玩家 ' + result[1][i] + ' 對你發起的對戰'):
										target(result[1][i])
										server.createroom(result[1][i], p_name)
									else:
										server.distarget(p_name, '2') # 拒絕邀請
						else:
							if (result[0][i] == p2_name) & (result[1][i] == '2'):
								tmp = p2_name
								p2_name = ''
								tkinter.messagebox.showinfo(title='對戰', message='玩家 ' + tmp + ' 拒絕對戰')
								server.distarget(tmp)
							create_player(self.canvas, result[0][i], result[1][i])
					for i in range(0, len(p_pos)):
						if p_pos[i].name not in p_now:
							p_pos[i].name = ''
							p_pos[i].i = 0
							p_pos[i].j = 0
					if flag == 0:
						time.sleep(1)
					else:
						window.switch_frame(moraface)

			def click(event): # 判斷點擊
				x = event.x
				y = event.y
				if ((60<x)&(x<820)) & ((40<y)&(y<500)):
					for i in range(0, 8):
						if ((i*100+60)<x) & (x<(i*100+120)):
							for j in range(0, 5):
								if ((j*100+40)<y) & (y<(j*100+100)):
									if p_pos[i+j*8].name != '':
										if tkinter.messagebox.askyesno(title='對戰', message='對玩家 '+ p_pos[i+j*8].name +' 發起對戰？'):
											target(p_pos[i+j*8].name)
											global p2_name
											p2_name = p_pos[i+j*8].name

		# 遊戲介面
		class moraface(tk.Frame): # 猜拳介面
			def __init__(self, root):
				tk.Frame.__init__(self, root, width=900, height=600)
				frame = tk.Frame(self, width=880, height=40, bg='#ADADAD')
				frame.place(x=12, y=10)
				global room_num
				room_num = server.getroomnum(p_name)
				self.room = tk.Label(frame, text='房 間 ： '+str(room_num+1), font=("",12), bg='#ADADAD')
				self.room.place(x=10, y=10)
				tk.Label(frame, text=' 猜 拳 ', font=("",12), bg='#ADADAD').place(x=400, y=10)

				self.canvas = tk.Canvas(self, bg="#CDCD9A" , width=880, height=540)
				self.canvas.place(x=10, y=50)

				img.append(tk.PhotoImage(file='Images/player.gif'))
				img.append(tk.PhotoImage(file='Images/0.gif'))
				img.append(tk.PhotoImage(file='Images/1.gif'))
				img.append(tk.PhotoImage(file='Images/2.gif'))
				img.append(tk.PhotoImage(file='Images/3.gif'))
				def bt_1():
					self.mora(1)
				def bt_2():
					self.mora(2)
				def bt_3():
					self.mora(3)
				
				self.canvas.create_image(775, 115, image = img[0])
				tk.Label(self.canvas, text=p2_name, font=("標楷體",15), fg='#2F0000', bg='#CDCD9A').place(x=710, y=24)
				self.canvas.create_image(505, 130, image = img[1])

				self.p2_c = tk.Label(self.canvas, text=p2_name + ' : ' + p2_c, font=("標楷體",20), bg='#CDCD9A')
				self.p2_c.place(x=60, y=60)
				self.say = tk.Label(self.canvas, text=gametext, font=("標楷體",25), bg='#CDCD9A')
				self.say.place(x=390, y=250)
				self.p1_c = tk.Label(self.canvas, text=p_name + ' : ' + p1_c, font=("標楷體",20), bg='#CDCD9A')
				self.p1_c.place(x=60, y=120)
				self.canvas.create_image(105, 425, image = img[0])
				tk.Label(self.canvas, text=p_name, font=("標楷體",15), fg='#2F0000', bg='#CDCD9A').place(x=40, y=490)
				bt1 = tk.Button(self.canvas, command=bt_1, image=img[2], width=100, height=100).place(x=250, y=350) # 剪刀
				bt2 = tk.Button(self.canvas, command=bt_2, image=img[3], width=100, height=100).place(x=450, y=400) # 石頭
				bt3 = tk.Button(self.canvas, command=bt_3, image=img[4], width=100, height=100).place(x=650, y=350) # 布

			def mora(self, cmd): #猜拳
				global room_num
				room_num = server.getroomnum(p_name)
				self.room.config(text='房 間 ： '+str(room_num+1))
				result = server.mora(room_num, p_name, cmd)
				global gametext, p1_c, p2_c
				if result[0] == 'TIE':
					p1_c = mora[result[1]]
					p2_c = mora[result[2]]
					gametext = '平手了，再猜一次'
					self.p1_c.config(text=p_name + ' : ' + p1_c)
					self.p2_c.config(text=p2_name + ' : ' + p2_c)
					self.say.config(text=gametext)
				else:
					p1_c = mora[result[1]]
					p2_c = mora[result[2]]
					gametext = '玩家 ' + result[0] + ' 猜拳猜贏了'
					window.switch_frame(udlrface)

		class udlrface(tk.Frame): # 猜方向介面
			def __init__(self, root):
				tk.Frame.__init__(self, root, width=900, height=600)
				frame = tk.Frame(self, width=880, height=40, bg='#ADADAD')
				frame.place(x=12, y=10)
				self.room = tk.Label(frame, text='房 間 ： '+str(room_num+1), font=("",12), bg='#ADADAD')
				self.room.place(x=10, y=10)
				tk.Label(frame, text=' 猜 方 向 ', font=("",12), bg='#ADADAD').place(x=400, y=10)

				self.canvas = tk.Canvas(self, bg="#CDCD9A" , width=880, height=540)
				self.canvas.place(x=10, y=50)

				img.append(tk.PhotoImage(file='Images/up.gif'))
				img.append(tk.PhotoImage(file='Images/down.gif'))
				img.append(tk.PhotoImage(file='Images/left.gif'))
				img.append(tk.PhotoImage(file='Images/right.gif'))
				def bt_1():
					self.udlr(1)
				def bt_2():
					self.udlr(2)
				def bt_3():
					self.udlr(3)
				def bt_4():
					self.udlr(4)
						
				self.canvas.create_image(775, 115, image = img[0])
				tk.Label(self.canvas, text=p2_name, font=("標楷體",15), fg='#2F0000', bg='#CDCD9A').place(x=710, y=24)
				self.canvas.create_image(528, 130, image = img[1])

				tk.Label(self.canvas, text=p2_name + ' : ' + p2_c, font=("標楷體",20), bg='#CDCD9A').place(x=60, y=60)
				tk.Label(self.canvas, text=gametext, font=("標楷體",25), bg='#CDCD9A').place(x=390, y=250)
				tk.Label(self.canvas, text=p_name + ' : ' + p1_c, font=("標楷體",20), bg='#CDCD9A').place(x=60, y=120)

				self.canvas.create_image(105, 425, image = img[0])
				tk.Label(self.canvas, text=p_name, font=("標楷體",15), fg='#2F0000', bg='#CDCD9A').place(x=40, y=490)
				bt1 = tk.Button(self.canvas, command=bt_1, image=img[5], width=100, height=100).place(x=250, y=350) # 上
				bt2 = tk.Button(self.canvas, command=bt_2, image=img[6], width=100, height=100).place(x=400, y=400) # 下
				bt3 = tk.Button(self.canvas, command=bt_3, image=img[7], width=100, height=100).place(x=550, y=400) # 左
				bt4 = tk.Button(self.canvas, command=bt_4, image=img[8], width=100, height=100).place(x=700, y=350) # 右
			
			def udlr(self, cmd): # 猜方向
				global room_num
				room_num = server.getroomnum(p_name)
				self.room.config(text='房 間 ： '+str(room_num+1))
				result = server.udlr(room_num, p_name, cmd)
				global gametext, p1_c, p2_c
				if result[0] == 'AGAIN':
					p1_c = udlr[result[1]]
					p2_c = udlr[result[2]]
					gametext = '方向不同，再一次'
					window.switch_frame(moraface)
				else:
					distarget()
					tkinter.messagebox.showinfo(title='遊戲', message='玩家 ' + result[0] + ' 獲勝')
					p1_c = ''
					p2_c = ''
					gametext = ''
					global p2_name
					p2_name = ''
					if result[0] == p_name:
						room_num = server.getroomnum(p_name)
						server.delroom(room_num)
					window.switch_frame(hallface)

		# 介面
		window = face()
		window.title('黑白配')
		center_window(window, 900, 600)
		window.resizable(width=0, height=0)
		
		window.protocol('WM_DELETE_WINDOW', window_close)
		window.mainloop()
	except Exception as e:
		print('Other exception: %s' % str(e))

# end of main

if __name__ == '__main__':
	main()
