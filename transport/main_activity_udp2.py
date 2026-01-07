#########################################################################
#file_name:main_activity_udp2.py
#UPDATE:2025/11/26
#name:hashimoto
#file_content:メインクラス
#########################################################################

import os          # OS関連の操作（画面クリア、シャットダウンなど）
import fx3u_udp as fx3u        # PLC通信クラス（電文作成と送受信）
import camera_c1 as camera     # カメラ制御・画像処理クラス
import socket
import threading   # マルチスレッド処理（複数の処理を並行実行）
import signal      # OSからの信号処理（Ctrl+Cなど）
import time        # 時間を扱う
import psycopg2    # PostgreSQLデータベース接続用（現在はコメントアウト）

import requests    # HTTPリクエスト用（ログサーバーへの通信などに使用）
import datetime    # 日付と時刻を扱う

class MainActivity:
    ##初期設定
    def __init__(self):
        os.system('cls')#コマンド画面クリア
        self.datetime_now = datetime.datetime.now()#現在日時を取得
        self.datetime_now = self.datetime_now.isoformat()#日付データを文字列に変換（ログ記録用）
        
        self.url = "http://192.168.1.2/ito_test/log.php?q="#エラーログ書込みプログラムのURL（サーバー側。現在はコメントアウト）
        
        self.is_main_finish = False#メインプログラム終了信号
        self.exit_signal = False   # OSからの終了信号（Ctrl+C）フラグ
        
        # スレッド設定: 4つの主要な処理を並行して動かす
        self.thread_plc = threading.Thread(target=self.communicate_plc)##PLC通信スレッド（PLCとの情報のやり取りを常時行う）
        self.thread_camera = threading.Thread(target=camera.manage_camera)##カメラ管理スレッド（カメラからの画像取得を常時行う）
        self.thread_hand = threading.Thread(target=camera.detect_hand)##手や身体の検出スレッド（危険エリアへの侵入監視）
        self.thread_image_processing = threading.Thread(target=camera.manage_image_processing)##画像処理スレッド（PLC指令を受けて各種検査を実行）
        
        # Ctrl+C (SIGINT) 信号を受け取った際のハンドラを設定
        signal.signal(signal.SIGINT, self.Handler)
        
        #スレッドをデーモン化
        # メインスレッドが終了したら、他のスレッドも強制的に終了させる設定
        self.thread_plc.setDaemon(True)
        self.thread_camera.setDaemon(True)
        self.thread_hand.setDaemon(True)
        self.thread_image_processing.setDaemon(True)

        #データベース接続先（現在はコメントアウト）
        #self.conn = psycopg2.connect(
        #    host="192.168.1.2",
        #    database="management_db",
        #    user="odd",
        #    password="odd"
        #)
        #self.cur = self.conn.cursor()

        self.is_oshidashi_state = True # 未使用フラグ
        self.is_fukuro_state = True    # 未使用フラグ
        self.is_kensa_state = True     # 未使用フラグ
        
        #実行モードファイルを作成し、初期値 '1' を書き込む
        path = 'C:/startfile/g52024/finish.txt' #ここ一致させないとエラーが起きる
        with open(path, mode='w') as f:
            f.write("1") # '1'は通常動作モードを意味すると想定
        
    
    #各スレッドをスタートし、終了信号が検出されるまで無限ループ
    def Run(self):
        ##各スレッドスタート
        self.thread_plc.start()
        self.thread_camera.start()
        self.thread_hand.start()
        self.thread_image_processing.start()
        
        #各処理の終了信号がFalseの間連続動作（メインスレッドは待機状態）
        while   not self.is_main_finish and  \
                not camera.is_manage_camera_finish:
            pass # 終了フラグが立つまで何もしない
        
        # 終了フラグが立った後の処理
        if camera.is_camera_shutdown:
            print("シャットダウンします")
            os.system('shutdown /s /t 1') # OSをシャットダウン
        else:
            print("プログラムを終了します")
            time.sleep(2)
        #os.system('shutdown /s /t 1')
            
    # Ctrl+C (SIGINT) 信号を受け取った際に呼び出される関数
    def Handler(self, signal, frame):
        self.exit_signal = True # 終了フラグをONにする
    
    #PLC通信（メインプログラム）
    # このスレッドが、PLCとのやり取りを行う心臓部
    def communicate_plc(self):
        # 起動時に各種カメラ許可信号を初期化（OFFにする）
        print(fx3u.write_bitdevice('M20', 0))
        print(fx3u.write_bitdevice('M21', 0))
        print(fx3u.write_bitdevice('M22', 0))
        print(fx3u.write_bitdevice('M155', 0))

        #現在日時をPLCに送信（時刻同期）
        dt_now = datetime.datetime.now()
        print(fx3u.write_worddevice('D50', 1, dt_now.year))#年 (Dデバイスに書き込み)
        print(fx3u.write_worddevice('D51', 1, dt_now.month))#月
        print(fx3u.write_worddevice('D52', 1, dt_now.day))#日
        print(fx3u.write_worddevice('D53', 1, dt_now.hour))#時
        print(fx3u.write_worddevice('D54', 1, dt_now.minute))#分
        print(fx3u.write_worddevice('D55', 1, dt_now.second))#秒
        time.sleep(3)
        print(fx3u.write_bitdevice('M55', 1)) # 時刻同期完了信号をON
        
        print("communicate_plcモジュール（PLC通信モジュール）が動作しました")
        
        state = 1 # 状態変数 (1: 正常状態, 2: エラー状態)
        path = 'C:/startfile/g52024/finish.txt'
        
        # PLCとの通信と処理監視を行う無限ループ
        while(1):
            try:
                start = time.time()#whileの1ループタイム測定スタート
                
                # 外部ファイルからシャットダウン/終了信号を読み込み
                with open(path) as f:
                    s = f.read()
                if s == '2': # 外部ファイルが '2' ならシャットダウン
                    print("シャットダウン信号が入りました")
                    break
                if s == '3': # 外部ファイルが '3' ならプログラム終了
                    print("プログラムを終了")
                    self.is_main_finish = True

                # PLCから現在の状態（デバイス値）を読み出し
                message_m = fx3u.read_bitdevice('M20')#M20～M23までの値を取得を取得(カメラ許可信号など)
                message_finish = fx3u.read_bitdevice('M154')#M154の値を取得(装置終了信号など)
                message_d = fx3u.read_worddevice('D91', 10)#D91～D100までの値を取得(エラー信号レジスタ)
                
                
                #PLC側にエラーが出たとき動作 (電文が初期値でない、かつ状態が正常(state=1)の場合)
                if message_d != '81000000000000000000000000000000000000000000' and state == 1:
                    print(message_d)
                    print("エラー発生")
                    error_id = 0
                    
                    # D91～D100の各ワードの値を見て、どの種類のエラーかを判定
                    if message_d[4:8] != '0000':
                        print("非常停止")
                        error_id = 1#非常停止
                    if message_d[8:12] != '0000':
                        error_id = 2#DC24Vモニタ
                        print("モニタ")
                    if message_d[12:16] != '0000':
                        error_id = 3#人体検知
                        print("人体検知")
                    if message_d[16:20] != '0000':
                        error_id = 4#一次空気圧力不足
                        print("圧力不足")
                    if message_d[20:24] != '0000':
                        error_id = 5#袋がない
                        print("袋なし")
                    if message_d[24:28] != '0000':
                        error_id = 6#パソコンの異常
                        print("パソコンの異常")
                    if message_d[28:32] != '0000':
                        error_id = 7#機器が異常
                        print("異常な入力の組み合わせ")
                    if message_d[32:36] != '0000':
                        error_id = 8
                        print("バッテリ残量低下")
                    if message_d[36:40] != '0000':
                        error_id = 9
                        print("稼働時間")
                    
                    #データベースに書き込み（現在はコメントアウト）
                    time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')#現在日時を取得
                    #self.cur.execute(
                    #    "INSERT INTO t_errorlog (error_id, errored_time, error_status) VALUES (" + str(error_id) + ", '" + time_stamp + "', FALSE)")
                    #self.conn.commit()
                    print("エラー情報をデータベースに書き込みました")
                    
                    state = 2#ステータスをエラー中（state=2）に変更
                
                #PLC側のエラーが解決したときに動作
                if state == 2:
                    # エラー信号レジスタ(D91-D100)が全て0に戻ったことを確認
                    if message_d == '81000000000000000000000000000000000000000000':
                        print("エラーが解除されました")
                        fx3u.write_bitdevice('M24', 0)#エラー解決信号（M24）をリセット

                        #エラー解決有無をTrueに上書き（現在はコメントアウト）
                        #self.cur.execute("UPDATE t_errorlog SET error_status = TRUE WHERE error_number = (SELECT MAX(error_number) FROM t_errorlog)")
                        #self.conn.commit()
                        print("エラー情報を上書きました")
                        
                        state = 1#ステータスをエラーなし（state=1）に変更

                
                # **カメラ検査の開始トリガー処理**
                # Mデバイスの値の特定のビットが'1'（ON）になったら、対応するカメラ検査を開始
                
                #押出部カメラ許可信号を受け取ったら動作 (M20)
                if message_m[4] == '1': # 読み出し電文のM20の位置（4文字目）が'1'なら
                    print("押し出し部のカメラ許可が出ました")
                    fx3u.write_bitdevice('M20', 0)#PLC側の許可信号をリセット（処理の重複を防ぐ）
                    camera.is_start_oshidashi = True#画像処理スレッドへ開始信号をON
                    
                #袋セット部カメラ許可信号を受け取ったら動作 (M21)
                if message_m[5] == '1':
                    print("袋セット部のカメラ許可が出ました")
                    fx3u.write_bitdevice('M21', 0)#カメラ許可信号をリセット
                    camera.is_start_fukuro = True#画像処理スレッドへ開始信号をON
                    
                #検査部カメラ許可信号を受け取ったら動作 (M22)
                if message_m[6] == '1':
                    print("検査部のカメラ許可が出ました")
                    fx3u.write_bitdevice('M22', 0)#カメラ許可信号をリセット
                    camera.is_start_kensa = True#画像処理スレッドへ開始信号をON
                    
                # **カメラ検査の結果フィードバック処理**
                
                #押出部の検査が完了したら動作
                if camera.is_send_oshidashi_result:
                    #fx3u.write_worddevice('D20', 1, camera.oshidashi_result)#押出部の検査結果を書込み（本来の結果値）
                    fx3u.write_worddevice('D20', 1, 1)#押出部の検査結果をD20に書込み（ここでは常に1を書き込んでいる）
                    camera.is_send_oshidashi_result = False#検査完了信号をリセット
                    
                #袋セット部の検査が完了したら動作
                if camera.is_send_fukuro_result:
                    #fx3u.write_worddevice('D21', 1, camera.fukuro_result)#袋セット部の検査結果を書込み
                    fx3u.write_worddevice('D21', 1, 1)#袋セット部の検査結果をD21に書込み
                    camera.is_send_fukuro_result = False#検査完了信号をリセット
                    
                #検査部の検査が完了したら動作
                if camera.is_send_kensa_result:
                    #fx3u.write_worddevice('D22', 1, camera.kensa_result)#検査部の検査結果を書込み
                    fx3u.write_worddevice('D22', 1, 1)#検査部の検査結果をD22に書込み
                    camera.is_send_kensa_result = False#検査完了信号をリセット
                    camera.is_ser_finish = False
                    
                       
                #押出部のワークセット完了後、装置内に手や身体を検出したら動作
                if camera.is_detect_hand:
                    fx3u.write_worddevice2('D23', 2, 1, 1) # D23に危険信号を書き込み
                    print("手が検出されました")
                else:
                    fx3u.write_worddevice2('D23', 2, 1, 1) # 手が検出されていない場合も同じ値を書き込んでいる（※修正が必要な可能性あり）
                
                #M155が1ならメインプログラム終了信号をTrueに
                if message_finish[5] == '1': # M155（装置終了信号）がONなら
                    camera.finish_cap_oshidashi = True # カメラの終了処理を起動
                    self.is_main_finish = True # メインループを終了
                    print("終了します")
                    #fx3u.finish_signal()
                    time.sleep(3)
                    print("正しく終了しました")
                    
                stop = time.time()#whileの1ループタイム測定終了
                #print(stop - start)#whileの1ループタイムを表示（処理速度のデバッグ用）
            
            #PLC通信モジュール例外処理（通信が途切れた、電文解析エラーなど）
            except:
                self.datetime_now = datetime.datetime.now()#現在日時を取得
                self.datetime_now = self.datetime_now.isoformat()#日付データを文字列に変換

                fx3u.write_worddevice('D24', 1, 2) # PLCのD24にエラーコード '2' を書き込み
                
                error_message = ":[Error] main_activity, communication error with PLC"#エラーメッセージを設定

                import traceback
                traceback.print_exc()#エラー詳細を表示
                self.is_main_finish = True#メインプログラム終了信号をTrueに（強制終了へ）
                print("メインプログラムでエラーが発生しました")

        print("終了処理に入ります")
        camera.is_camera_shutdown = True # カメラ管理スレッドに終了を通知
        print("全てのモジュールが終了しました")
        print("安全にシャットダウン処理に入ります")
        self.is_main_finish = True
               
# メインプログラムのエントリーポイント
if __name__ == '__main__':
    print("メインプログラムを開始します")
    #time.sleep(1)

    fx3u = fx3u.Fx3u(socket.gethostbyname(socket.gethostname()), 50000, 4096) #仮想 #fx3u通信クラスをインスタンス化（ローカルホスト）
    # fx3u = fx3u.Fx3u("192.168.1.250", 5000, 4096) #実機 #fx3u通信クラスをインスタンス化（実機/仮想PLCのIPアドレス）
    camera = camera.Camera()#カメラ制御クラスをインスタンス化
    main_activity = MainActivity()#メインクラスをインスタンス化
    main_activity.Run() # プログラム実行開始