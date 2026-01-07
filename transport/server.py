##############################################
#2024/09/14
#Ito Natsuki
#PLCの模擬環境
##############################################

import datetime
import socket
import os
import time
import cv2


PORT = 50000
BUFSIZE = 4096
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
    
D100 = '0000'

#01. Socket Making : socket()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#02. Address & Port : bind()
server.bind(ADDR)
#03. Waiting the connection : listen()
server.listen()

device_M = ['0'] * 8000
device_D = ['0000'] * 8000



try:
    while True :
        
        #print("---------------------------------------------------------")
        #print(f'[NEW Connection] {ADDR} connected.')

        # 04. Getting the socket : accept()
        client, addr = server.accept()

        # 05. Data Yaritori : send(), recv()
        # 確認
        #msg = str(datetime.datetime.now())
        #print(f'{msg} : 接続要求あり')

        #print(client)

        #クライアントより受信
        data = client.recv(BUFSIZE)

        if data.decode(FORMAT) == '00000000':
            response_msg = "8100"
            client.sendall(response_msg.encode(FORMAT))
            time.sleep(1)
            break
        
        
        #電文種類
        msg_kind = data.decode(FORMAT)[:12]

        #ビット読み取り
        if msg_kind == '00FF000A4D20':
            #応答メッセージ
            response_msg = "8000"
            #デバイス番号
            msg_device = data.decode(FORMAT)[16:20]
            #デバイス番号をint型に変換
            msg_device_int = int(msg_device, 16)
            #デバイス点数をint型に変換
            msg_device_num = int(data.decode(FORMAT)[20:22], 16)
            #デバイスに格納されているデータを表示
            for i in range(msg_device_num):
                response_msg = response_msg + device_M[msg_device_int]
                #print("M" + str(msg_device_int) + " の値は " + device_M[msg_device_int] + " です")
                msg_device_int = msg_device_int + 1
            
            #print(msg)
            client.sendall(response_msg.encode(FORMAT))

        #ワード読み取り
        if msg_kind == '01FF000A4420':
            #応答メッセージ
            response_msg = "8100"
            #デバイス番号
            msg_device = data.decode(FORMAT)[16:20]

            #if msg_device == '0064':
            #デバイス番号をint型に変換
            msg_device_int = int(msg_device, 16)
            #デバイス点数をint型に変換
            msg_device_num = int(data.decode(FORMAT)[20:22], 16)
            #デバイスに格納されているデータを表示
            for i in range(msg_device_num):
                response_msg = response_msg + device_D[msg_device_int]
                #print("D" + str(msg_device_int) + " の値は " + device_D[msg_device_int] + " です")
                msg_device_int = msg_device_int + 1
            
            
            #print(msg)
            client.sendall(response_msg.encode(FORMAT))
        
        #ビット書き込み
        if msg_kind == '02FF000A4D20':
            #応答メッセージ
            response_msg = "8100"
            #デバイス番号
            msg_device = data.decode(FORMAT)[16:20]

            #デバイス番号を16進int型に変換
            msg_device_int = int(msg_device, 16)
            #デバイス点数を16進int型に変換
            msg_device_num = int(data.decode(FORMAT)[20:22], 16)
            range_first = 24
            range_last = 25
            #デバイスに格納されているデータを表示
            for i in range(msg_device_num):
                #書き込むデータを抽出
                msg_data = data.decode(FORMAT)[range_first:range_last]
                device_M[msg_device_int] = msg_data
                #print("M" + str(msg_device_int) + " に " + device_M[msg_device_int] + " を書き込みました")
                range_first = range_first + 1
                range_last = range_last + 1
                msg_device_int = msg_device_int + 1
                
            client.sendall(response_msg.encode(FORMAT))
        
        #ワード書き込み
        if msg_kind == '03FF000A4420':
            #デバイス番号
            msg_device = data.decode(FORMAT)[16:20]

            #デバイス番号を16進int型に変換
            msg_device_int = int(msg_device, 16)
            #デバイス点数を16進int型に変換
            msg_device_num = int(data.decode(FORMAT)[20:22], 16)
            range_first = 24
            range_last = 28
            #デバイスに格納されているデータを表示
            for i in range(msg_device_num):
                #書き込むデータを抽出
                msg_data = data.decode(FORMAT)[range_first:range_last]
                device_D[msg_device_int] = msg_data
                #print("D" + str(msg_device_int) + " に " + device_D[msg_device_int] + " を書き込みました")
                range_first = range_first + 4
                range_last = range_last + 4
                msg_device_int = msg_device_int + 1

            
            client.sendall("ワード書込み成功".encode(FORMAT))

        #print(data.decode(FORMAT))
        
        if msg_kind != '00FF000A4D20':
            os.system('cls')
            #print("デバイスM20～M22")
            print("デバイスM20 : " + device_M[20] + device_M[21] + device_M[22] + device_M[23] + device_M[24] + device_M[25] + device_M[26] + device_M[27] + device_M[28])
            print()
            #print("デバイスD20～D22")
            print("デバイスD20 : " + device_D[20])
            print("デバイスD21 : " + device_D[21])
            print("デバイスD22 : " + device_D[22])
            print("デバイスD23 : " + device_D[23])
            print()
            print("デバイスD93 : " + device_D[93])



except KeyboardInterrupt:
    print('Finished!')