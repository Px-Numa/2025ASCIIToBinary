#########################################################################
#file:camera_c1.py
#date:2025/11/25
#name:橋本
#file_content:fx3uシリーズ伝文コマンド
#UPDATE: 2025/11/25 解説追加
#########################################################################

import cv2      # 画像処理ライブラリ（OpenCV）
import time     # 時間を扱う
import numpy as np # 数値計算ライブラリ（行列計算などに使用）
import mediapipe as mp # 手や身体を検出するライブラリ
from matplotlib import pyplot as plt # グラフ描画ライブラリ（今回は未使用）

import random
import requests # サーバー通信用
import datetime # 日付と時刻を扱う
import serial   # シリアル通信（ラベル貼り機など外部機器と通信するため）


class Camera:
    ##初期設定---------------------------------------------------------------------------------------------------------------
    def __init__(self):
        # 画像のファイルパスを設定
        # 処理結果の画像や、検査範囲を指定するためのマスク画像を保存する場所
        self.output_oshidashi_image_filepath = "C:/startfile/g52024/image/output_oshidashi_image.jpg"
        self.output_fukuro_image_filepath = "C:/startfile/g52024/image/output_fukuro_image.jpg"
        self.output_qr_image_filepath = "C:/startfile/g52024/image/output_qr_image.jpg"
        self.output_kensa1_image_filepath = "C:/startfile/g52024/image/output_kensa1_image.jpg"
        self.output_kensa2_image_filepath = "C:/startfile/g52024/image/output_kensa2_image.jpg"
        self.output_kensa3_image_filepath = "C:/startfile/g52024/image/output_kensa3_image.jpg"
        self.output_kensa4_image_filepath = "C:/startfile/g52024/image/output_kensa4_image.jpg"
        
        self.file_path_nitika = "C:/startfile/g52024/image/nitika.jpg" # 2値化画像の保存パス（デバッグ用）
        self.file_path_rinkaku = "C:/startfile/g52024/image/rinkaku.jpg" # 輪郭画像の保存パス（デバッグ用）
        self.file_path_result = "C:/startfile/g52024/image/result.jpg" # 最終結果画像の保存パス（デバッグ用）
        
        # 検査範囲を限定するためのマスク画像ファイルのパス
        self.mask_oshidashi_filepath = "C:/startfile/g52024/image/mask_oshidashi.jpg" # 押出部で検査する範囲を限定
        self.mask_fukuro_filepath = "C:/startfile/g52024/image/mask_fukuro.jpg"
        self.mask_kensa1_filepath = "C:/startfile/g52024/image/mask_kensa1.jpg"
        self.mask_kensa2_filepath = "C:/startfile/g52024/image/mask_kensa2.jpg"
        self.mask_kensa3_filepath = "C:/startfile/g52024/image/mask_kensa3.jpg"
        self.mask_kensa4_filepath = "C:/startfile/g52024/image/mask_kensa4.jpg"
        self.hansya_filepath = "C:/startfile/g52024/image/hansya_mask.jpg" # 袋の反射を除去するために使うグレー画像
        
        # mediapipe設定
        # 手の検出に必要なツールを準備
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        
        # 各検査モジュールの開始信号（メインプログラムから「検査開始！」の指令が来るとTrueになる）
        self.is_start_oshidashi = False    # 押出部
        self.is_start_fukuro = False       # 袋セット部
        self.is_start_kensa = False        # 検査部
        self.is_start_qr = False           # QR読取り部
        self.is_start_detect_hand = False  # 手検出部
        
        # 各検査モジュールの検査終了信号（検査が終わったらメインプログラムに知らせるためにTrueにする）
        self.is_send_oshidashi_result = False # 押出部
        self.is_send_fukuro_result = False    # 袋セット部
        self.is_send_kensa_result = False     # 検査部
        self.is_detect_hand = False           # 手が検出されたかどうか
        self.is_ser_finish = False            # ラベル貼り終了信号
        
        # 各検査モジュールの検査結果（1:OK/あり, 2:NG/なし など）
        self.oshidashi_result = 0 # 押出部
        self.fukuro_result = 0    # 袋セット部
        self.kensa_result = 0     # 検査部
        
        # 各モジュールの終了信号
        self.is_manage_camera_finish = False

        # シャットダウン時の終了信号
        self.is_camera_shutdown = False          # カメラクラス全体終了信号
        self.is_manage_camera_shutdown = False
        self.is_detect_hand_shutdown = False
        self.is_manage_image_processing = False
        
        # カメラ初期化（現在はコメントアウトされており、静止画を読み込んでシミュレーションしている）
        # PCを起動するたびにCapture番号が変わってしまうので、毎回Capture番号を調べる必要がある
        # やり方としては、それぞれのカメラで特定の場所を読取り、映った色やQRコードなどで判別する方法がよさそう
        # 他言語を使用してポート番号を取得するのも出来そうである
        #ポートの識別はシリアル通信　C言語使うかも　USBポート　デバイス番号出てきて使う場合もある
        #self.cap_oshidashi = cv2.VideoCapture(3)#押出部カメラ
        #self.cap_fukuro = cv2.VideoCapture(1)#袋セット部カメラ
        #self.cap_qr = cv2.VideoCapture(2)#qr部カメラ
        #self.cap_kensa1 = cv2.VideoCapture(3)#検査部カメラ左上
        #self.cap_kensa2 = cv2.VideoCapture(4)#検査部カメラ右上
        #self.cap_kensa3 = cv2.VideoCapture(5)#検査部カメラ左下
        #self.cap_kensa4 = cv2.VideoCapture(6)#検査部カメラ右下

        #self.cap_oshidashi.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)#押出部カメラのサイズ
        #self.cap_fukuro.set(cv2.CAP_PROP_FRAME_WIDTH, 640)#袋セット部カメラのサイズ


        # 押出部のカメラ調整（露出やフォーカス設定）
        #self.cap_oshidashi.set(cv2.CAP_PROP_AUTOFOCUS, 0)#フォーカス自動調整をオフ
        #self.cap_oshidashi.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)#露出自動調整をオフ
        #self.cap_oshidashi.set(cv2.CAP_PROP_EXPOSURE, -7) # 露出値を手動設定
        """
        袋セットのカメラ調整
        self.cap_fukuro.set(cv2.CAP_PROP_AUTOFOCUS, 0)#フォーカス自動調整をオフ
        self.cap_fukuro.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)#露出自動調整をオフ
        self.cap_fukuro.set(cv2.CAP_PROP_EXPOSURE, -8)
        
        #QR読み取りのカメラ調整
        cap3.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)#露出自動調整をオン
        cap3.set(cv2.CAP_PROP_AUTOFOCUS, 1)#フォーカス自動調整をオン
        """

        self.datetime_now = datetime.datetime.now() # 現在日時を取得
        self.datetime_now = self.datetime_now.isoformat() # 日付データを文字列に変換
        
        self.url = "http://192.168.1.2/ito_test/log.php?q=" # エラーログ書込みプログラムのURL（サーバー側）

        self.is_start_ser = True # シリアル通信（ラベル貼り機）の初期化フラグ

        # 押出カメラ表示ウインドウの終了信号
        self.finish_cap_oshidashi = False
        
        
        
            
    ##カメラ起動、画像撮影-------------------------------------------------------------------------------------------------------
    def manage_camera(self):
        print("manage_cameraモジュール（カメラ管理モジュール）が動作しました")
        
        # 各カメラの画像をファイルから読み込み、フレームとして代入（※実際のカメラではなく、静止画で模擬動作させている）
        self.frame_oshidashi = cv2.imread("C:/startfile/g52024/image/oshidashi_image.jpg", 1)
        self.frame_fukuro = cv2.imread("C:/startfile/g52024/image/fukuro_image.jpg", 1)
        self.frame_qr = cv2.imread("C:/startfile/g52024/image/qr_image.jpg", 1)
        self.frame_kensa1 = cv2.imread("C:/startfile/g52024/image/kensa1_image.jpg", 1)
        self.frame_kensa2 = cv2.imread("C:/startfile/g52024/image/kensa2_image.jpg", 1)
        self.frame_kensa3 = cv2.imread("C:/startfile/g52024/image/kensa3_image.jpg", 1)
        self.frame_kensa4 = cv2.imread("C:/startfile/g52024/image/kensa4_image.jpg", 1)
        
        while(1):
            #time.sleep(0.1)
            #self.cap_oshidashi.set(cv2.CAP_PROP_EXPOSURE, -8)
            try:
                if self.is_camera_shutdown:
                    break
                
                ## 各カメラから画像を取得（※本来はここで行うが、現在はコメントアウト）
                #ret1, self.frame_oshidashi = self.cap_oshidashi.read()
                #ret2, self.frame_fukuro = self.cap_fukuro.read()
                #ret3, self.frame_qr = self.cap_qr.read()
                #ret4, self.frame_kensa1 = self.cap_kensa1.read()
                #ret5, self.frame_kensa2 = self.cap_kensa2.read()
                #ret6, self.frame_kensa3 = self.cap_kensa3.read()
                #ret7, self.frame_kensa4 = self.cap_kensa4.read()
                #if ret1 == False:
                #    break
                
                # if(self.finish_cap_oshidashi): # メインプログラム終了時にカメラを解放
                #    self.cap_oshidashi.release()
                    #self.cap_fukuro.release()
                    #self.cap_qr.release()
                    #self.cap_kensa1.release()
                    #self.cap_kensa2.release()
                    #self.cap_kensa3.release()
                    #self.cap_kensa4.release()
                #    cv2.destroyAllWindows()
                #    time.sleep(5)

                # cv2.imshow('oshidashi', self.frame_oshidashi) # カメラ画像をウィンドウに表示（デバッグ用）
                # cv2.imshow('fukuro', self.frame_fukuro)
                # cv2.imshow('qr', self.frame_qr)
                # cv2.imshow('左上', self.frame_kensa1)
                # cv2.imshow('右上', self.frame_kensa2)
                # cv2.imshow('左下', self.frame_kensa3)
                # cv2.imshow('右下', self.frame_kensa4)

                key = cv2.waitKey(1) # キー入力待ち
                
            # manage_cameraの例外処理（カメラの接続不良など）
            except:
                self.datetime_now = datetime.datetime.now() # 現在日時を取得
                self.datetime_now = self.datetime_now.isoformat() # 日付データを文字列に変換
                #error_message = ":[Error] manage_camera, communication error with camera"#エラーメッセージを設定（ログ記録用）
                #response = requests.get(self.url + self.datetime_now + error_message)#エラーログ書込みプログラムを実行（GETで日付データとエラーメッセージを送信）
                #print (response.elapsed.total_seconds())
                import traceback
                traceback.print_exc() # エラーの詳細を表示
                self.is_manage_camera_finish = True # 画像撮影プログラム終了信号をTrueに
                print("画像撮影プログラム(while中の例外)でエラーが発生しました")
                time.sleep(5)

        print("manage_cameraモジュール（カメラ管理モジュール）を終了します")
        self.is_manage_camera_shutdown = True # シャットダウン信号をTrueに

        # カメラの接続不良が起こったら動作
        self.datetime_now = datetime.datetime.now() # 現在日時を取得
        self.datetime_now = self.datetime_now.isoformat() # 日付データを文字列に変換
        #error_message = ":[Error] manage_camera, communication error with camera"#エラーメッセージを設定（ログ記録用）
        #response = requests.get(self.url + self.datetime_now + error_message)#エラーログ書込みプログラムを実行（GETで日付データとエラーメッセージを送信）
        #print (response.elapsed.total_seconds())
        import traceback
        #traceback.print_exc()
        #self.is_manage_camera_finish = True#画像撮影プログラム終了信号をTrueに
        #print("画像撮影プログラムでエラーが発生しました")
        #time.sleep(5)
            
            
    ##手や身体の検出-------------------------------------------------------------------------------------------------------------
    def detect_hand(self):
        ## カメラが最初の画像を取得するまで待機
        time.sleep(5)
        print("detect_handモジュール（手検出モジュール）が動作しました")
        self.is_detect_hand = False
        #cv2.namedWindow('hands', cv2.WINDOW_NORMAL)
        
        mask = cv2.imread(self.mask_oshidashi_filepath, 1) # 押出部のマスク画像を読み込み
        
        # MediaPipe Handsモデルの設定（min_detection_confidence=0.01で検出精度をほぼ0にし、少しでも手の形があれば検出する）
        with self.mp_hands.Hands(static_image_mode=True,
            max_num_hands=2, # 検出する手の数（最大2まで）
            min_detection_confidence=0.01) as hands:
            while(1):
                self.is_detect_hand = False
                try:
                    if self.is_camera_shutdown:
                        break

                    image = cv2.cvtColor(self.frame_oshidashi, cv2.COLOR_BGR2RGB) # 画像をMediaPipeが使うRGB形式に変換
                    imagea = cv2.cvtColor(self.frame_oshidashi, cv2.COLOR_BGR2RGB) # 描画用にオリジナルも保持
                    image.flags.writeable = False

                    image = cv2.bitwise_and(image, mask) # マスク処理（検査エリア外は無視）

                    # 推論処理
                    hands_results = hands.process(image) # MediaPipeで手の検出を実行

                    # 前処理の変換を戻しておく。
                    image.flags.writeable = True
                    write_image = cv2.cvtColor(imagea, cv2.COLOR_RGB2BGR)

                    # 手が検出された場合、
                    if hands_results.multi_hand_landmarks:
                        # 検出した手の特徴点（ランドマーク）を画像に描画（デバッグ用）
                        for landmarks in hands_results.multi_hand_landmarks:
                            self.mp_drawing.draw_landmarks(
                                write_image,
                                landmarks,
                                self.mp_hands.HAND_CONNECTIONS,
                                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                self.mp_drawing_styles.get_default_hand_connections_style())

                        self.is_detect_hand = True # 手が検出されたことを示す信号をON
                    else:
                        self.is_detect_hand = False # 手が検出されていない
                    
                    # ディスプレイ表示
                    #cv2.imshow('hands', write_image)

                    key = cv2.waitKey(1)


                except:
                    self.is_detect_hand = True # エラー発生時も安全のため検出ありとしておく
                    #print("予期せぬエラー（手判定）")

            print("detect_handモジュール（手検出モジュール）を終了します")
            self.is_detect_hand_shutdown = True # シャットダウン信号をTrueに
    
    
    ##画像処理の動作管理-------------------------------------------------------------------------------------------------------
    def manage_image_processing(self):
        ## カメラが最初の画像を取得するまで待機
        time.sleep(5)
        print("manage_image_processingモジュール（画像処理動作モジュール）が動作しました")
        #self.read_qr(self.frame_oshidashi)#ラベル貼りを動作する際にコメントアウト（現在はQR読み取りをスキップ）
        while(1):
            time.sleep(0.1)
            if self.is_camera_shutdown:
                break
            
            #ファイルアクセスを行うと0.1秒ほど時間がかかってしまう
            #各モジュールではデバッグのため画像を保存しているが、本番環境ではいらないかも
            
            # 押出部の開始信号がTrueになったら動作
            if self.is_start_oshidashi:
                start = time.time() # 時間測定開始
                
                self.judge_oshidashi(self.frame_oshidashi) # 押出部のワーク有無判定モジュールの実行
                self.is_send_oshidashi_result = True       # 押出部終了信号をTrueに
                self.is_start_oshidashi = False            # 押出部開始信号をFalseに
                
                stop = time.time() # 時間測定終了
                print("押し出し部の検査にかかった時間は")
                print(stop - start)
                print("-------------------------------------------------")
                
            # 袋セット部の開始信号がTrueになったら動作
            if self.is_start_fukuro:
                start = time.time() # 時間測定開始
                
                self.judge_fukuro(self.frame_fukuro) # 袋セット部の袋有無判定モジュールの実行
                self.is_send_fukuro_result = True     # 袋セット部終了信号をTrueに
                self.is_start_fukuro = False          # 袋セット部開始信号をFlaseに
                
                stop = time.time() # 時間測定終了
                print("袋セット部の検査にかかった時間は")
                print(stop - start)
                print("-------------------------------------------------")
                
            # 検査部の開始信号がTrueになったら動作
            if self.is_start_kensa:
                start = time.time() # 時間測定開始
                
                # 4つの検査カメラの画像に対して、袋穴あき検査モジュールを順次実行
                self.judge_kensa(self.frame_kensa1, self.output_kensa1_image_filepath, self.mask_kensa1_filepath)
                self.judge_kensa(self.frame_kensa2, self.output_kensa2_image_filepath, self.mask_kensa2_filepath)
                self.judge_kensa(self.frame_kensa3, self.output_kensa3_image_filepath, self.mask_kensa3_filepath)
                self.judge_kensa(self.frame_kensa4, self.output_kensa4_image_filepath, self.mask_kensa4_filepath)
                
                print(self.read_qr(self.frame_qr)) # QR読取りモジュールの実行
                
                stop = time.time() # 時間測定終了
                print("検査部の検査にかかった時間は")
                print(stop - start)
                print("-------------------------------------------------")
                
                self.is_send_kensa_result = True # 検査部終了信号をTrueに
                self.is_start_kensa = False      # 検査部開始信号をFalseに

        print("manage_image_processingモジュール（画像処理動作モジュール）を終了します")
        self.is_manage_image_processing = True # シャットダウン信号をTrueに
    
    
    ##押出部のワーク有無判定------------------------------------------------------------------------------------------------------
    def judge_oshidashi(self, image):
        print("押出部のワーク有無判定")
        
        mask = cv2.imread(self.mask_oshidashi_filepath, 0) # 押出部のマスク画像の読み込み
        #size = (1920, 1080)#画像サイズ
        size = (640, 480) # 画像サイズ
        image = cv2.resize(image, size) # カメラ画像をリサイズ
        mask = cv2.resize(mask,size)  # マスク画像をリサイズ
        image_size = image.shape[0] * image.shape[1] # 画像全体の面積を算出
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # グレースケールに変換
        image = cv2.bitwise_and(image, mask) # マスク処理（検査エリア外を無視）
        
        # 2値化処理（閾値89: この値より明るい画素を白(255)に、暗い画素を黒(0)にする）
        thresh_value, image_area = cv2.threshold(image, 89, 255, cv2.THRESH_BINARY)
        
        whitePixels = cv2.countNonZero(image_area) # 白色の部分（ワークがない部分）の画素数を算出
        blackPixels = image_size - whitePixels # 黒色の部分（ワークがある部分）の画素数を算出
    
        whiteAreaRatio = (whitePixels/image_size) * 100 # 白色の部分の割合を算出
        blackAreaRatio = (blackPixels/image_size) * 100 # 黒色の部分の割合を算出
    
        print("White Area [cm2] : ", whiteAreaRatio)
        print("Black Area [cm2] : ", blackAreaRatio)
        
        cv2.imwrite("image/oshidashi_result.jpg", image_area) # 処理後画像を保存（デバッグ用）
        
        if whiteAreaRatio >= 24.45: # 白い部分の割合が24.45%以上ならワークセットOK
            self.oshidashi_result = 1 # ワークセットOK
            print("ワークセットOK")
        else:
            self.oshidashi_result = 2 # ワークセットNG
            print("ワークセットNG")
    
    
    ##袋セット部の袋の有無判定---------------------------------------------------------------------------------------------------
    def judge_fukuro(self, image):
        print("袋セット部の袋の有無判定")
        
        mask = cv2.imread(self.mask_fukuro_filepath, 0) # 袋セット部のマスク画像の読み込み
        size = (640, 480) # 画像サイズ
        image = cv2.resize(image, size) # カメラ画像をリサイズ
        mask = cv2.resize(mask,size) # マスク画像をリサイズ
        image_size = image.shape[0] * image.shape[1] # 画像サイズの面積を算出
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # グレースケールに変換
        image = cv2.bitwise_and(image, mask) # マスク処理
        
        # 2値化処理（閾値200: 袋の明るい部分を検出）
        thresh_value, image_area = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
        
        whitePixels = cv2.countNonZero(image_area) # 白色の部分（袋がある部分）の画素数を算出
        blackPixels = image_size - whitePixels # 黒色の部分を算出
    
        whiteAreaRatio = (whitePixels/image_size) * 100 # 白色の部分の割合を算出
        blackAreaRatio = (blackPixels/image_size) * 100 # 黒色の部分の割合を算出
    
        print("White Area [cm2] : ", whiteAreaRatio)
        print("Black Area [cm2] : ", blackAreaRatio)
        
        #cv2.imwrite("image/fukuro_result.jpg", image_area)#処理後画像を保存
        
        if whiteAreaRatio >= 5: # 白い部分の割合が5%以上なら袋あり
            self.fukuro_result = 1 # 袋あり
            print("袋あり")
        else:
            self.fukuro_result = 2 # 袋なし
            print("袋なし")
        
        
    ##検査部の袋の破れ有無判定----------------------------------------------------------------------------------------------------
    def judge_kensa(self, image, path, mask_filepath):
        print("検査部の袋の破れ有無判定")
        
        # 画像読み込み
        image_color = image # カメラのカラー画像
        mask = cv2.imread(mask_filepath, 0) # 袋の角マスク画像
        hansya = cv2.imread(self.hansya_filepath, 0) # 反射除去用のグレー画像
        
        # 画像サイズの変更
        size = (640,480) # 画像サイズ
        image = cv2.resize(image, size)
        image_color = cv2.resize(image_color, size)
        mask = cv2.resize(mask, size)
        hansya = cv2.resize(hansya, size)
        
        image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) # グレー画像に変換
        
        # 反射除去のための前処理 ----------------------------------------------
        thresh_value, nitika_image = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY) # 明るい部分（反射）を白として取得
        hihanten = nitika_image     # 反射部分が白の画像
        hanten = 255 - nitika_image # 反射部分が黒の画像
        
        # 元画像から反射部分を切り取る
        nitika_image = cv2.bitwise_and(image, hanten) 
        
        # グレー画像から反射部分の形に合わせて切り取る
        hansya = cv2.bitwise_and(hansya, hihanten) 
        
        # 切り取った反射部分をグレー画像に差し替え（反射を除去）
        nitika_image = cv2.add(nitika_image, hansya) 
        #cv2.imwrite("C:/startfile/g52024/image/hansya.jpg", nitika_image)#反射をなくした画像を表示（デバッグ用）
        # ------------------------------------------------------------------
        
        image = nitika_image
        
        ## 平滑化（ノイズ除去）
        image = cv2.medianBlur(image, 5) # メディアンフィルタを3回適用してノイズを大幅に除去
        image = cv2.medianBlur(image, 5)
        image = cv2.medianBlur(image, 5)

        ## エッジ処理
        th1 = 94
        th2 = 23
        nitika_image = cv2.Canny(image, th1, th2) # Canny法でエッジ（輪郭）を検出
        #cv2.imwrite("C:/startfile/g52024/image/canny.jpg", nitika_image)#反射をなくした画像を表示（デバッグ用）

        nitika_image = cv2.bitwise_and(nitika_image, mask) # マスク処理（検査範囲外のエッジを無視）
        
        ## 輪郭検出----------------------------------------------------------------------
        nitika_image_color = cv2.cvtColor(nitika_image,cv2.COLOR_GRAY2BGR) # カラー画像に変換
        #ret,thresh = cv2.threshold(nitika_image, 63, 255, cv2.THRESH_BINARY)#白黒のエリアを決定
        
        # 輪郭を検出（RETR_EXTERNAL: 一番外側の輪郭だけを検出）
        contours,hierarchy = cv2.findContours(nitika_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 検出した輪郭を描画（デバッグ用）
        contimg = cv2.drawContours(nitika_image_color, contours, -1, (0, 255, 0), 7)
        
        ## 穴あきを検出（ラベリング処理）-------------------------------------------------------------
        contimg_gray = cv2.cvtColor(contimg, cv2.COLOR_BGR2GRAY) # 輪郭画像をグレー画像に変換
        thresh_value, image = cv2.threshold(contimg_gray, 100, 255, cv2.THRESH_BINARY) # 輪郭部分を白色に
        
        # ラベリング処理（つながった白い領域（＝穴あきの輪郭）にそれぞれ番号を振る）
        nlabel, image_label = cv2.connectedComponents(image) 
        
        self.kensa_result = 1 # 初期値は破れなし(1)
        # ラベリングされた各領域をチェック
        for i in range(1, nlabel):
            image_dst = cv2.compare(image_label, i, cv2.CMP_EQ) # 該当のラベル領域だけを抽出
            x, y, w, h = cv2.boundingRect(image_dst) # その領域を囲む矩形（四角）を算出
            
            # ある程度大きい矩形（高さhが20ピクセル以上）を穴あきと判定
            if h >= 20:
                #cv2.rectangle(image_color, (x,y), (x+w, y+h), (0,0,240), 3)#穴あき部分を囲む（デバッグ用）
                self.kensa_result = 2 # 破れあり(2)
                print("穴あきあり")
        #cv2.imwrite("C:/startfile/g52024/image/image_color.jpg", image_color)#ラベリング画像を保存（デバッグ用）
        
        
        
    ##QRコード読み取り
    def read_qr(self, image):
        print("QRを読み取ります")
        #ser = serial.Serial("COM5", 9600) # ここのポート番号を変更（ラベル貼り機とのシリアル通信）
        #val = 100 # ここの値を変更すると、Arduinoの挙動が変わる
        #time.sleep(13)
        #return "1111, aaa, 111"
        #"""
        
        # QRCodeDetectorオブジェクトを作成
        detector = cv2.QRCodeDetector()
        
        # 画像を切り取り、リサイズしてQRコードの検出をしやすくする
        image = image[450:670,900:1120]
        image = cv2.resize(image, (400,400))
        
        cv2.imwrite("C:/startfile/g52024/image/image_qr.jpg", image)
        
        print("QRコード読取り")
        try:
            # QRコードを検出し、デコード（情報を取り出す）
            retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(image)
            
            ## QRコードの文字列を表示
            print(decoded_info[0])
            print("QR読取り完了")
            
            ## 区切り文字指定（カンマで文字列を分割）
            dem = decoded_info[0].split(',')

            ## QRコードに意味のない半角スペースが入っているので除去
            ## QRコードの仕様を企業としっかり話し合う必要有
            dem_space = dem[0].split('　')
            print(dem_space[0])
            dem_space = dem[1].split('　')
            print(dem_space[0])
            dem_space = dem[2].split('　')
            print(dem_space[0])
            dem_space = dem[3].split('　')
            print(dem_space[0])
            dem_space = dem[4].split(' ')
            print(dem_space[0])
            
            # 最終日に気付いたが、生産商品情報登録するプログラムを作るのを忘れていた
            # 本来であればこの行に、QRコードから取得した情報をもとにデータベースに書込む処理を入れる
            
        
        except:
            import traceback
            traceback.print_exc()
        
        return#ラベル貼りを使用する際にコメントアウト（273行目も）
        # ラベル貼り装置自体はきちんと動作するが、通信などのエラー処理をしていないので自動運転に組み込むのはまだ怖い
        # 最終プログラムではあるが、動作するか不安なので実行前にreturnしている
        # 最後まで作りこみが甘いのは申し訳ないと思っている
        if self.is_start_ser:
            self.is_start_ser = False
            print("ラベル貼りと接続します")
            self.ser = serial.Serial("COM5", 9600)#ポート番号が違う場合はこの部分を変更する
            print("初期動作を終了します")
        elif self.is_ser_finish:
            pass
        else:
            print("動作開始")
            self.ser.write(bytes('1','utf-8')) # ラベル貼り機に「1」という指令を送信
            print("送信完了")

            time.sleep(15)

            #while val_arduino != '2': # ラベル貼り機からの完了信号を待つループ（現在はコメントアウト）
            #    try:
            #        val_arduino = self.ser.readline()
            #        print("2を受け取りました")
            #    except:
            #        print("例外")
                
            print("終了")
            self.is_ser_finish = True
            #self.ser.close()
        return