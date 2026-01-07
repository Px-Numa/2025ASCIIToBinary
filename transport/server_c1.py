##############################################
#2024/09/14
#Ito Natsuki
#server.py
#PLCの模擬環境
##############################################

import datetime # 日付と時刻を扱う（デバッグコメントで使用）
import socket   # ネットワーク通信（ソケット）を扱うライブラリ
import os       # OS機能（画面クリアなど）を扱う
import time     # 時間を扱う
import cv2      # OpenCV（ここでは未使用だがインポートされている）


PORT = 50000                            # サーバーが待ち受けるポート番号（FX3Uの通信ポート）
BUFSIZE = 4096                          # 受信バッファの最大サイズ
SERVER = socket.gethostbyname(socket.gethostname()) # サーバーのIPアドレス（実行しているPCのIPアドレス）
ADDR = (SERVER, PORT)                   # サーバーのアドレス情報 (IPアドレス, ポート番号)
FORMAT = 'utf-8'                        # データエンコーディング形式（電文はlatin-1だが、ここでは応答メッセージに使用）
    
D100 = '0000' # 未使用

#01. Socket Making : socket()
# AF_INET: IPv4, SOCK_STREAM: TCP通信ソケットを作成
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#02. Address & Port : bind()
# ソケットにサーバーのアドレス(IP/ポート)を割り当て
server.bind(ADDR)
#03. Waiting the connection : listen()
# 接続待ち状態へ移行（最大接続数を指定可能だが、省略時はデフォルト値）
server.listen()

# PLCデバイスのメモリを模擬するためのリスト
# Mデバイス（ビット）のメモリ: 8000点分を初期値 '0'（OFF）で確保
device_M = ['0'] * 8000 
# Dデバイス（ワード）のメモリ: 8000点分を初期値 '0000'（ゼロ）で確保（16進数4桁）
device_D = ['0000'] * 8000 



try:
    # 接続を永遠に待ち続けるメインループ
    while True :
        
        #print("---------------------------------------------------------")
        #print(f'[NEW Connection] {ADDR} connected.')

        # 04. Getting the socket : accept()
        # クライアントからの接続要求を待ち、接続が確立したら専用ソケット(client)とクライアントアドレス(addr)を取得
        client, addr = server.accept()

        # 05. Data Yaritori : send(), recv()
        # クライアント（メインプログラム）から電文を受信
        data = client.recv(BUFSIZE)

        # 終了信号の判定（特殊な電文 '00000000' を受信した場合）
        if data.decode(FORMAT) == '00000000':
            response_msg = "8100" # 終了応答メッセージ（FX3Uの応答コード）
            client.sendall(response_msg.encode(FORMAT))
            time.sleep(1)
            break # サーバーのループを終了
        
        
        # 電文種類（通信の目的）を電文の先頭12文字で判定
        msg_kind = data.decode(FORMAT)[:12]

        # ビット読み取り (Mデバイス読み出し指令: '00FF000A4D20')
        if msg_kind == '00FF000A4D20':
            #応答メッセージの初期値
            response_msg = "8000" # ビット読み出し成功時の応答コード
            #電文からデバイス番号（先頭アドレス）を抽出
            msg_device = data.decode(FORMAT)[16:20]
            #デバイス番号を16進数から整数(int)に変換
            msg_device_int = int(msg_device, 16)
            #デバイス点数を16進数から整数(int)に変換
            msg_device_num = int(data.decode(FORMAT)[20:22], 16)
            
            #要求された点数分だけメモリからデータを取得し、応答メッセージに連結
            for i in range(msg_device_num):
                response_msg = response_msg + device_M[msg_device_int]
                #print("M" + str(msg_device_int) + " の値は " + device_M[msg_device_int] + " です")
                msg_device_int = msg_device_int + 1
            
            #print(msg)
            client.sendall(response_msg.encode(FORMAT)) # クライアントに応答を送信

        # ワード読み取り (Dデバイス読み出し指令: '01FF000A4420')
        if msg_kind == '01FF000A4420':
            #応答メッセージの初期値
            response_msg = "8100" # ワード読み出し成功時の応答コード
            #電文からデバイス番号（先頭アドレス）を抽出
            msg_device = data.decode(FORMAT)[16:20]

            #デバイス番号を16進数から整数(int)に変換
            msg_device_int = int(msg_device, 16)
            #デバイス点数を16進数から整数(int)に変換
            msg_device_num = int(data.decode(FORMAT)[20:22], 16)
            
            #要求された点数分だけメモリからデータを取得し、応答メッセージに連結
            for i in range(msg_device_num):
                response_msg = response_msg + device_D[msg_device_int] # Dデバイスの値は4桁の16進数文字列
                #print("D" + str(msg_device_int) + " の値は " + device_D[msg_device_int] + " です")
                msg_device_int = msg_device_int + 1
            
            
            #print(msg)
            client.sendall(response_msg.encode(FORMAT)) # クライアントに応答を送信
        
        # ビット書き込み (Mデバイス書き込み指令: '02FF000A4D20')
        if msg_kind == '02FF000A4D20':
            #応答メッセージの初期値
            response_msg = "8100" # 書き込み成功時の応答コード
            #電文からデバイス番号（先頭アドレス）を抽出
            msg_device = data.decode(FORMAT)[16:20]

            #デバイス番号を16進数から整数(int)に変換
            msg_device_int = int(msg_device, 16)
            #デバイス点数を16進数から整数(int)に変換
            msg_device_num = int(data.decode(FORMAT)[20:22], 16)
            
            # 電文から書き込みデータが始まる位置を設定
            range_first = 24
            range_last = 25
            
            #要求された点数分だけメモリにデータを書き込む
            for i in range(msg_device_num):
                #書き込むデータ（'0'または'1'）を電文から抽出
                msg_data = data.decode(FORMAT)[range_first:range_last]
                device_M[msg_device_int] = msg_data # Mデバイスメモリに値を格納
                #print("M" + str(msg_device_int) + " に " + device_M[msg_device_int] + " を書き込みました")
                range_first = range_first + 1 # 次のビットデータへ移動
                range_last = range_last + 1
                msg_device_int = msg_device_int + 1
                
            client.sendall(response_msg.encode(FORMAT)) # クライアントに応答を送信
        
        # ワード書き込み (Dデバイス書き込み指令: '03FF000A4420')
        if msg_kind == '03FF000A4420':
            #電文からデバイス番号（先頭アドレス）を抽出
            msg_device = data.decode(FORMAT)[16:20]

            #デバイス番号を16進数から整数(int)に変換
            msg_device_int = int(msg_device, 16)
            #デバイス点数を16進数から整数(int)に変換
            msg_device_num = int(data.decode(FORMAT)[20:22], 16)
            
            # 電文から書き込みデータが始まる位置を設定
            range_first = 24
            range_last = 28
            
            #要求された点数分だけメモリにデータを書き込む
            for i in range(msg_device_num):
                #書き込むデータ（4桁の16進数）を電文から抽出
                msg_data = data.decode(FORMAT)[range_first:range_last]
                device_D[msg_device_int] = msg_data # Dデバイスメモリに値を格納
                #print("D" + str(msg_device_int) + " に " + device_D[msg_device_int] + " を書き込みました")
                range_first = range_first + 4 # 次のワードデータへ移動（ワードは4文字分）
                range_last = range_last + 4
                msg_device_int = msg_device_int + 1

            
            client.sendall("ワード書込み成功".encode(FORMAT)) # クライアントに成功応答を送信

        #print(data.decode(FORMAT))
        
        # Mデバイスのビット読み取り時以外は画面をクリアし、現在のデバイス値を表示（モニタリング）
        if msg_kind != '00FF000A4D20':
            os.system('cls') # コマンドプロンプト画面をクリア
            # モニタリング対象のMデバイスの値を連結して表示
            print("デバイスM20 : " + device_M[20] + device_M[21] + device_M[22] + device_M[23] + device_M[24] + device_M[25] + device_M[26] + device_M[27] + device_M[28])
            print()
            # モニタリング対象のDデバイスの値を表示
            print("デバイスD20 : " + device_D[20])
            print("デバイスD21 : " + device_D[21])
            print("デバイスD22 : " + device_D[22])
            print("デバイスD23 : " + device_D[23])
            print()
            print("デバイスD93 : " + device_D[93])


except KeyboardInterrupt:
    print('Finished!') # Ctrl+Cでプログラムを終了した場合のメッセージ