#########################################################################
#file:fx3u.py
#date:2024/09/20
#name:伊東
#file_content:fx3uシリーズ伝文コマンド
#########################################################################

##自作の伝文作成プログラムなので動作保証はできない
##このようにやれば伝文送信できるようになる、くらいには役に立ちそうである
##使用からきちんと作って汎用性の高いライブラリを作ることが出来たら素晴らしい

import socket
import time

class Fx3u:
    
    ##Fx3uクラス初期設定
    ##(self, 相手IPアドレス(String), 相手ポート番号(int), 送信サイズ(int))
    def __init__(self, ip, port, bufsize):
        self.ip = ip
        self.port = port
        self.bufsize = bufsize
        
    
    ##終了信号
    def finish_signal(self):
        try:
            print("終了信号を送信します")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.ip, self.port))

            msg = '00000000'
            msg = msg.encode('latin-1')
            client.send(msg)
            ##PLCからの返信情報
            response = client.recv(1024)

            response = response.decode()

            client.close()
            print("終了信号が正しく送信されました")
        
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")

    ##読出し(ワード単位)
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int))
    def read_worddevice(self, device, device_point):
        try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.connect((self.ip, self.port))
            
            ##デバイス種類指定
            if device[0:1] == 'M':
                msg = '00FF000A4D20'
                
            elif device[0:1] == 'D':
                msg = '01FF000A4420'
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            ##デバイス点数指定
            msg = msg + format(int(device_point), '02x') + '00'
            ##バイト型に変換
            msg = msg.encode('latin-1')
            #print(type(msg))

            ##PLCに送信
            client.send(msg)
            ##PLCからの返信情報
            response = client.recv(1024)
            response = response.decode()
            client.close()
            return response
        
        
            
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")
    
    ##読出し(ビット単位)
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
                msg = '00FF000A4D20'
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            ##デバイス点数指定
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
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int), 書込み内容(int))  
    def write_worddevice(self, device, device_point, write_content):
        #try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.ip, self.port))
            
            ##デバイス種類指定
            if device[0:1] == 'M':
                msg = '02FF000A4D20'
                
            elif device[0:1] == 'D':
                msg = '03FF000A4420'
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            ##デバイス点数指定
            msg = msg + format(int(device_point), '02x') + '00'
            #書き込み内容
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
    ##本来であれば1点の時と2点の時でモジュールを返るのは良くないが、面倒くさかったので別モジュールにした
    def write_worddevice2(self, device, device_point, write_content1, write_content2):
        try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.ip, self.port))
            
            ##デバイス種類指定
            if device[0:1] == 'M':
                msg = '02FF000A4D20'
                
            elif device[0:1] == 'D':
                msg = '03FF000A4420'
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            ##デバイス点数指定
            msg = msg + format(int(device_point), '02x') + '00'
            #書き込み内容
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
                msg = '02FF000A4D20'
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            ##デバイス点数指定
            msg = msg + '0400'
            #書き込み内容
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
            