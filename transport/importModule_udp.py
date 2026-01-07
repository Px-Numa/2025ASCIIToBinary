#########################################################################
#file:importModule_udp.py
#date:2024/09/20
#name:橋本
#file_content:
#このファイルはPLCからの信号を書き換えれる
#pythonのサーバを立てながらここを編集する
#main_activity.pyはこのファイルを書き換えるときは起動させない

#UPDATE: 2025/11/25 (UDP通信に変更)
##########################################################

import fx3u_udp as fx3u
import socket
import time
import datetime

#fx3u = fx3u.Fx3u(socket.gethostbyname(socket.gethostname()), 50000, 4096) #仮想
fx3u = fx3u.Fx3u("192.168.1.254", 5000, 4096) #実機

#print(fx3u.write_worddevice2('D25', 2, 1, 1))

#time.sleep(10)
print(fx3u.write_bitdevice('M20', 1))
time.sleep(1)
print(fx3u.write_bitdevice('M21', 1))
time.sleep(1)
print(fx3u.write_bitdevice('M22', 1))
time.sleep(2)
#print(fx3u.write_bitdevice('M154', 1))
print(fx3u.write_bitdevice('M155', 1))
#print(fx3u.write_bitdevice('M23', 0))
#print(fx3u.write_bitdevice('M28', 1))
#print(fx3u.read_bitdevice('M0'))

#print(fx3u.write_bitdevice('M24', 1))
#print(fx3u.write_worddevice('D91', 1, 0))
#message_d = fx3u.read_worddevice('D20', 2)
#print(message_d)

#print(message_d[28:32])
#print(message_d[32:36])

#print(fx3u.read_bitdevice('M24'))

#dt_now = datetime.datetime.now()
#print(dt_now)

#dt_year = dt_now.year


#print(fx3u.write_worddevice('D50', 1, dt_year))
#print(fx3u.write_worddevice('D51', 1, 2))
#print(fx3u.write_worddevice('D52', 1, 7))
#print(fx3u.write_worddevice('D53', 1, 15))
#print(fx3u.write_worddevice('D54', 1, 26))
#print(fx3u.write_worddevice('D55', 1, 30))
#print(fx3u.write_worddevice('D56', 1, 5))
#time.sleep(1)
#print(fx3u.write_bitdevice('M55', 1))