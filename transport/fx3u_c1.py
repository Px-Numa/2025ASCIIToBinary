#########################################################################
#file:fx3u.py
#date:2024/09/20
#name:伊東
#file_content:fx3uシリーズ伝文コマンド
#########################################################################

##自作の伝文作成プログラムなので動作保証はできない
##このようにやれば伝文送信できるようになる、くらいには役に立ちそうである
##使用からきちんと作って汎用性の高いライブラリを作ることが出来たら素晴らしい

import socket # TCP/IP通信を行うためのライブラリ
import time   # 時間を扱うライブラリ

class Fx3u:
    
    ##Fx3uクラス初期設定
    ##(self, 相手IPアドレス(String), 相手ポート番号(int), 送信サイズ(int))
    def __init__(self, ip, port, bufsize):
        # 接続先のPLCのIPアドレス
        self.ip = ip
        # 接続先のPLCのポート番号 (例: 50000)
        self.port = port
        # 受信バッファの最大サイズ
        self.bufsize = bufsize
        
    
    ##終了信号
    # 通信セッションを安全に終了させるための特別な電文を送信する
    def finish_signal(self):
        try:
            print("終了信号を送信します")
            # TCP/IPソケットを作成
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # PLCへ接続を試みる
            client.connect((self.ip, self.port))

            msg = '00000000' # FX3U向けの終了指令電文（8桁のゼロ）
            msg = msg.encode('latin-1') # メッセージをバイト列に変換
            client.send(msg) # PLCに送信
            
            ##PLCからの返信情報（応答）
            response = client.recv(1024)

            response = response.decode() # バイト列を文字列にデコード

            client.close() # ソケットを閉じる
            print("終了信号が正しく送信されました")
        
        except ConnectionRefusedError:
            print("PLCに接続できませんでした") # 接続エラー時の処理

    ##読出し(ワード単位)
    ##ワード単位（16ビット）のデバイスを複数点読み出す
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int))
    def read_worddevice(self, device, device_point):
        try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP通信は今回は使用しない
            client.connect((self.ip, self.port))
            
            ##デバイス種類指定（読み出し電文の先頭部分を決定）
            if device[0:1] == 'M':
                # Mデバイス（補助リレー）の読み出し指令コード
                msg = '00FF000A4D20' 
                
            elif device[0:1] == 'D':
                # Dデバイス（データレジスタ）の読み出し指令コード
                msg = '01FF000A4420'
            
            ##先頭デバイス指定
            # デバイス番号（例: 'D20'の'20'）を整数に変換し、8桁の16進数文字列にする
            msg = msg + format(int(device[1:4]), '08x')
            
            ##デバイス点数指定
            # 読み出し点数を2桁の16進数に変換し、末尾に'00'を付加
            msg = msg + format(int(device_point), '02x') + '00'
            
            ##バイト型に変換
            msg = msg.encode('latin-1')
            #print(type(msg))

            ##PLCに送信
            client.send(msg)
            
            ##PLCからの返信情報（応答とデータ）
            response = client.recv(1024)
            response = response.decode()
            client.close()
            return response
        
        
            
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")
    
    ##読出し(ビット単位)
    ##ビット単位のデバイスを読み出す（主にON/OFF状態の確認）
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str))
    def read_bitdevice(self, device):
        try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.connect((self.ip, self.port))
            
            ##デバイス種類指定
            if device[0:1] == 'M':
                # Mデバイス（補助リレー）の読み出し指令コード (ワード読み出しと同じコードを使用)
                msg = '00FF000A4D20' 
            
            ##先頭デバイス指定
            # デバイス番号を整数に変換し、8桁の16進数文字列にする
            msg = msg + format(int(device[1:4]), '08x')
            
            ##デバイス点数指定
            # ビット読み出しの場合、点数は'0400'（4点）に固定されている
            msg = msg + '0400'
            
            ##バイト型に変換
            msg = msg.encode('latin-1')

            ##PLCに送信
            client.send(msg)

            ##PLCからの返信情報
            response = client.recv(1024)

            response = response.decode()

            client.close()
            
            return response
            
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")
        
    ##書込み(ワード単位)
    ##ワード単位（16ビット）のデバイスに1点分のデータを書き込む
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int), 書込み内容(int))  
    def write_worddevice(self, device, device_point, write_content):
        #try: # エラー処理がコメントアウトされているため、処理を継続
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.ip, self.port))
            
            ##デバイス種類指定（書き込み電文の先頭部分を決定）
            if device[0:1] == 'M':
                # Mデバイスへのビット書き込み指令コード
                msg = '02FF000A4D20'
                
            elif device[0:1] == 'D':
                # Dデバイスへのワード書き込み指令コード
                msg = '03FF000A4420'
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            
            ##デバイス点数指定
            msg = msg + format(int(device_point), '02x') + '00'
            
            #書き込み内容（整数値を4桁の16進数文字列に変換。ワードは16ビット=4桁16進数）
            msg = msg + format(int(write_content), '04x')
            
            #バイト型に変換
            msg = msg.encode('latin-1')

            #PLCに送信
            client.send(msg)

            #PLCからの返信情報
            response = client.recv(1024)

            response = response.decode()

            client.close()
            ##PLCからの返信を戻り値に
            return response
            
        #except ConnectionRefusedError:
        #    print("PLCに接続できませんでした")

    ##書込み(ワード単位)
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int), 書込み内容(int))  
    ##デバイス点数が2点の時に使用する
    ##本来であれば1点の時と2点の時でモジュールを分けるのは良くないが、面倒くさかったので別モジュールにした
    def write_worddevice2(self, device, device_point, write_content1, write_content2):
        try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.ip, self.port))
            
            ##デバイス種類指定
            if device[0:1] == 'M':
                msg = '02FF000A4D20'
                
            elif device[0:1] == 'D':
                msg = '03FF000A4420' # Dデバイスへのワード書き込み指令
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            
            ##デバイス点数指定 (ここでは2点として処理)
            msg = msg + format(int(device_point), '02x') + '00'
            
            #書き込み内容（1点目と2点目のデータを連結）
            msg = msg + format(int(write_content1), '04x')
            msg = msg + format(int(write_content2), '04x')
            
            #バイト型に変換
            msg = msg.encode('latin-1')

            #PLCに送信
            client.send(msg)

            #PLCからの返信情報
            response = client.recv(1024)

            response = response.decode()

            client.close()
            ##PLCからの返信を戻り値に
            return response
            
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")
            
            
    ##書込み(ビット単位)
    ##ビット単位のデバイスに1点分のデータを書き込む
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int), 書込み内容(int))  
    def write_bitdevice(self, device, write_content):
        try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.connect((self.ip, self.port))
            
            ##デバイス種類指定
            if device[0:1] == 'M':
                msg = '02FF000A4D20' # Mデバイスへのビット書き込み指令コード
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            
            ##デバイス点数指定
            # ビット書き込みの場合、点数は'0400'（4点）に固定されている
            msg = msg + '0400'
            
            #書き込み内容（ビット値 0 または 1 の後、パディングとして '000' を付加）
            msg = msg + str(write_content) +'000'
            
            #バイト型に変換
            msg = msg.encode('latin-1')

            #PLCに送信
            client.send(msg)

            #PLCからの返信情報
            response = client.recv(4096)

            response = response.decode()

            client.close()
            ##PLCからの返信を戻り値に
            return response
            
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")