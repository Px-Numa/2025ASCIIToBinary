#########################################################################
#file:fx3u_udp.py
#date:2024/09/20
#name:橋本
#file_content:fx3uシリーズ伝文コマンド
#UPDATE: 2025/11/17 (UDP通信に変更)
#########################################################################

##自作の伝文作成プログラムなので動作保証はできない
##このようにやれば伝文送信できるようになる、くらいには役に立ちそうである
##使用からきちんと作って汎用性の高いライブラリを作ることが出来たら素晴らしい

import socket # ネットワーク通信（ソケット）を扱うライブラリ
import time   # 時間を扱うライブラリ

class Fx3u:
    #Fx3uクラス初期設定
    #(self, 相手IPアドレス(String), 相手ポート番号(int), 送信サイズ(int), local_port(int)=PCの受信ポート, timeout=float秒)
    def __init__(self, ip, port, bufsize, local_port=None, timeout=5.0):
        self.ip = ip       # 接続先のPLCのIPアドレス（宛先）
        self.port = port   # 接続先のPLCのポート番号（宛先）
        self.bufsize = bufsize # 受信バッファの最大サイズ（受信可能データの上限）
        self.local_port = local_port # PC側の待ち受けポート（PLCのENET設定で合わせる5
        self.timeout = timeout # ソケットのタイムアウト（秒）
        
    
    ##終了信号
    # 通信セッションを安全に終了させるための特別な電文を送信する
    def finish_signal(self):
        try:
            print("終了信号を送信します")
            # 変更点: TCP(SOCK_STREAM)からUDP(SOCK_DGRAM)に変更
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDPソケットを作成
            # 必要に応じてローカルポートにバインド（PLCのENET設定でPCポートを固定している場合）
            if self.local_port is not None:
                client.bind(('', self.local_port))
            client.settimeout(self.timeout)

            msg = '00000000' # FX3U向けの終了指令電文（8桁のゼロ）
            msg = msg.encode('latin-1') # メッセージをバイト列に変換（FX3Uプロトコルに合わせたエンコーディング）
            
            # 変更点: send()からsendto()に変更し、宛先（IPとポート）を一緒に指定
            client.sendto(msg, (self.ip, self.port))
            
            ##PLCからの返信情報 (recvfromを使用し、データとアドレスを取得)
            try:
                response, addr = client.recvfrom(self.bufsize) # 応答データと送信元アドレス(addr)を受け取る
                response = response.decode() # バイト列を文字列にデコード
            except socket.timeout:
                print("PLC応答がタイムアウトしました")
                response = ""
            finally:
                client.close() # ソケットを閉じる

            if response:
                print("終了信号が正しく送信されました")
        
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")

    ##読出し(ワード単位)
    ##ワード単位（16ビット）のデバイスを複数点読み出す
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int))
    def read_worddevice(self, device, device_point):
        try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if self.local_port is not None:
                client.bind(('', self.local_port))
            client.settimeout(self.timeout)
            
            ##デバイス種類指定（読み出し電文の先頭部分を決定）
            if device[0:1] == 'M':
                msg = '00FF000A4D20' # Mデバイス（ビット）の読み出し指令コード
                
            elif device[0:1] == 'D':
                msg = '01FF000A4420' # Dデバイス（ワード）の読み出し指令コード
            
            ##先頭デバイス指定
            # デバイス番号（例: 'D20'の'20'）を8桁の16進数文字列に変換
            msg = msg + format(int(device[1:4]), '08x') 
            
            ##デバイス点数指定
            # 読み出し点数を2桁の16進数に変換し、末尾に'00'を付加
            msg = msg + format(int(device_point), '02x') + '00' 
            
            ##バイト型に変換
            msg = msg.encode('latin-1')
            #print(type(msg))

            ##PLCに送信
            # 変更点: send()からsendto()に変更し、宛先を指定
            client.sendto(msg, (self.ip, self.port))
            
            ##PLCからの返信情報 (recvfromを使用)
            try:
                response, addr = client.recvfrom(self.bufsize) # 応答データと送信元アドレス(addr)を受け取る
                response = response.decode()
            except socket.timeout:
                print("PLC応答がタイムアウトしました")
                response = ""
            finally:
                client.close()
            return response # PLCからの応答電文全体を返す
        
        
            
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")
    
    ##読出し(ビット単位)
    ##ビット単位（ON/OFF状態）のデバイスを読み出す
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str))
    def read_bitdevice(self, device):
        try:
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if self.local_port is not None:
                client.bind(('', self.local_port))
            client.settimeout(self.timeout)
            
            ##デバイス種類指定
            if device[0:1] == 'M':
                msg = '00FF000A4D20' # Mデバイス（ビット）の読み出し指令コード
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            
            ##デバイス点数指定
            # ビット読み出しの場合、点数指定は'0400'（4点）に固定されている
            msg = msg + '0400' 
            
            ##バイト型に変換
            msg = msg.encode('latin-1')

            ##PLCに送信
            # 変更点: send()からsendto()に変更し、宛先を指定
            client.sendto(msg, (self.ip, self.port))

            ##PLCからの返信情報 (recvfromを使用)
            try:
                response, addr = client.recvfrom(self.bufsize)
                response = response.decode()
            except socket.timeout:
                print("PLC応答がタイムアウトしました")
                response = ""
            finally:
                client.close()
            
            return response
            
        except ConnectionRefusedError:
            print("PLCに接続できませんでした")
        
    ##書込み(ワード単位)
    ##ワード単位（16ビット）のデバイスにデータを書き込む
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int), 書込み内容(int))  
    def write_worddevice(self, device, device_point, write_content):
        #try: # 本来はここでConnectionRefusedErrorなどをキャッチする
            ##PLCとソケット通信
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if self.local_port is not None:
                client.bind(('', self.local_port))
            client.settimeout(self.timeout)
            
            ##デバイス種類指定
            if device[0:1] == 'M':
                msg = '02FF000A4D20' # Mデバイスへのビット書き込み指令コード
                
            elif device[0:1] == 'D':
                msg = '03FF000A4420' # Dデバイスへのワード書き込み指令コード
            
            ##先頭デバイス指定
            msg = msg + format(int(device[1:4]), '08x')
            
            ##デバイス点数指定
            msg = msg + format(int(device_point), '02x') + '00'
            
            #書き込み内容
            # 整数値を4桁の16進数文字列に変換（ワードは16ビット）
            msg = msg + format(int(write_content), '04x') 
            
            #バイト型に変換
            msg = msg.encode('latin-1')

            #PLCに送信
            # 変更点: send()からsendto()に変更し、宛先を指定
            client.sendto(msg, (self.ip, self.port))

            #PLCからの返信情報 (recvfromを使用)
            try:
                response, addr = client.recvfrom(self.bufsize)
                response = response.decode()
            except socket.timeout:
                print("PLC応答がタイムアウトしました")
                response = ""
            finally:
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
        ##PLCとソケット通信
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.local_port is not None:
            client.bind(('', self.local_port))
        client.settimeout(self.timeout)
        
        ##デバイス種類指定
        if device[0:1] == 'M':
            msg = '02FF000A4D20'
            
        elif device[0:1] == 'D':
            msg = '03FF000A4420' # Dデバイスへのワード書き込み指令コード
        
        ##先頭デバイス指定
        msg = msg + format(int(device[1:4]), '08x')
        
        ##デバイス点数指定
        msg = msg + format(int(device_point), '02x') + '00' # デバイス点数を指定
        
        #書き込み内容
        msg = msg + format(int(write_content1), '04x')
        msg = msg + format(int(write_content2), '04x')
        
        #バイト型に変換
        msg = msg.encode('latin-1')

        #PLCに送信
        client.sendto(msg, (self.ip, self.port))

        #PLCからの返信情報 (recvfromを使用)
        try:
            response, addr = client.recvfrom(self.bufsize)
            response = response.decode()
        except socket.timeout:
            print("PLC応答がタイムアウトしました")
            response = ""
        finally:
            client.close()
        return response
            
            
    ##書込み(ビット単位)
    ##ビット単位（ON/OFF）のデバイスにデータを書き込む
    ##PLCからの返信を戻り値
    ##read(デバイス番号(str), デバイス点数(int), 書込み内容(int))  
    def write_bitdevice(self, device, write_content):
        ##PLCとソケット通信
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.local_port is not None:
            client.bind(('', self.local_port))
        client.settimeout(self.timeout)
        
        ##デバイス種類指定
        if device[0:1] == 'M':
            msg = '02FF000A4D20' # Mデバイスへのビット書き込み指令コード
        
        ##先頭デバイス指定
        msg = msg + format(int(device[1:4]), '08x')
        
        ##デバイス点数指定
        msg = msg + '0400'
        
        #書き込み内容
        msg = msg + str(write_content) +'000'
        
        #バイト型に変換
        msg = msg.encode('latin-1')

        #PLCに送信
        client.sendto(msg, (self.ip, self.port))

        #PLCからの返信情報 (recvfromを使用)
        try:
            response, addr = client.recvfrom(self.bufsize)
            response = response.decode()
        except socket.timeout:
            print("PLC応答がタイムアウトしました")
            response = ""
        finally:
            client.close()
        return response