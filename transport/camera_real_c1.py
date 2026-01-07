#########################################################################
#file_name:camera.py
#date:2024/12/18
#name:伊東
#file_content:カメラクラス
#
#update:2025/01/06
#name:伊東
#update_content:袋破れ検査モジュールの修正（フィルタ処理と閾値の変更）
#
#update:2025/03/05
#name:伊東
#update_content:最終確認
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
        #画像のファイルパスを設定
        self.output_oshidashi_image_filepath = "C:/startfile/g52024/image/output_oshidashi_image.jpg"
        self.output_fukuro_image_filepath = "C:/startfile/g52024/image/output_fukuro_image.jpg"
        self.output_qr_image_filepath = "C:/startfile/g52024/image/output_qr_image.jpg"
        self.output_kensa1_image_filepath = "C:/startfile/g52024/image/output_kensa1_image.jpg"
        self.output_kensa2_image_filepath = "C:/startfile/g52024/image/output_kensa2_image.jpg"
        self.output_kensa3_image_filepath = "C:/startfile/g52024/image/output_kensa3_image.jpg"
        self.output_kensa4_image_filepath = "C:/startfile/g52024/image/output_kensa4_image.jpg"
        
        self.file_path_nitika = "C:/startfile/g52024/image/nitika.jpg"
        self.file_path_rinkaku = "C:/startfile/g52024/image/rinkaku.jpg"
        self.file_path_result = "C:/startfile/g52024/image/result.jpg"
        
        self.mask_oshidashi_filepath = "C:/startfile/g52024/image/mask_oshidashi.jpg"
        self.mask_fukuro_filepath = "C:/startfile/g52024/image/mask_fukuro.jpg"
        self.mask_kensa1_filepath = "C:/startfile/g52024/image/mask_kensa1.jpg"
        self.mask_kensa2_filepath = "C:/startfile/g52024/image/mask_kensa2.jpg"
        self.mask_kensa3_filepath = "C:/startfile/g52024/image/mask_kensa3.jpg"
        self.mask_kensa4_filepath = "C:/startfile/g52024/image/mask_kensa4.jpg"
        self.hansya_filepath = "C:/startfile/g52024/image/hansya_mask.jpg"
        
        #mediapipe設定
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        
        #各検査モジュールの開始信号
        self.is_start_oshidashi = False#押出部
        self.is_start_fukuro = False#袋セット部
        self.is_start_kensa = False#検査部
        self.is_start_qr = False#QR読取り部
        self.is_start_detect_hand = False#手検出部
        
        #各検査モジュールの検査終了信号
        self.is_send_oshidashi_result = False#押出部
        self.is_send_fukuro_result = False#袋セット部
        self.is_send_kensa_result = False#検査部
        self.is_detect_hand = False#手検出部
        self.is_ser_finish = False#ラベル貼り終了信号
        
        #各検査モジュールの検査結果
        self.oshidashi_result = 0#押出部
        self.fukuro_result = 0#袋セット部
        self.kensa_result = 0#検査部
        
        #各モジュールの終了信号
        self.is_manage_camera_finish = False

        #シャットダウン時の終了信号
        self.is_camera_shutdown = False#カメラクラス全体終了信号
        self.is_manage_camera_shutdown = False
        self.is_detect_hand_shutdown = False
        self.is_manage_image_processing = False
        
        #カメラ初期化 (Webカメラからのリアルタイム処理を有効化)
        #PCを起動するたびにCapture番号が変わってしまうので、毎回Capture番号を調べる必要がある
        #今回は面倒くさかったのでやっていない
        #やり方としては、それぞれのカメラで特定の場所を読取り、映った色やQRコードなどで判別する方法がよさそう
        #他言語を使用してポート番号を取得するのも出来そうである
        self.cap_oshidashi = cv2.VideoCapture(3)#押出部カメラ
        self.cap_fukuro = cv2.VideoCapture(1)#袋セット部カメラ
        self.cap_qr = cv2.VideoCapture(2)#qr部カメラ
        self.cap_kensa1 = cv2.VideoCapture(3)#検査部カメラ左上
        self.cap_kensa2 = cv2.VideoCapture(4)#検査部カメラ右上
        self.cap_kensa3 = cv2.VideoCapture(5)#検査部カメラ左下
        self.cap_kensa4 = cv2.VideoCapture(6)#検査部カメラ右下

        self.cap_oshidashi.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)#押出部カメラのサイズ
        self.cap_fukuro.set(cv2.CAP_PROP_FRAME_WIDTH, 640)#袋セット部カメラのサイズ


        #押出部のカメラ調整
        self.cap_oshidashi.set(cv2.CAP_PROP_AUTOFOCUS, 0)#フォーカス自動調整
        self.cap_oshidashi.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)#露出自動調整
        self.cap_oshidashi.set(cv2.CAP_PROP_EXPOSURE, -7)
        """
        袋セットのカメラ調整
        self.cap_fukuro.set(cv2.CAP_PROP_AUTOFOCUS, 0)#フォーカス自動調整
        self.cap_fukuro.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)#露出自動調整
        self.cap_fukuro.set(cv2.CAP_PROP_EXPOSURE, -8)
        
        #QR読み取りのカメラ調整
        cap3.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)#露出自動調整
        cap3.set(cv2.CAP_PROP_AUTOFOCUS, 1)#フォーカス自動調整
        """

        self.datetime_now = datetime.datetime.now()#現在日時を取得
        self.datetime_now = self.datetime_now.isoformat()#日付データを文字列に変換
        
        self.url = "http://192.168.1.2/ito_test/log.php?q="#エラーログ書込みプログラムのURL（サーバー側）

        self.is_start_ser = True

        #押出カメラ表示ウインドウの終了信号
        self.finish_cap_oshidashi = False
        
        
        
            
    ##カメラ起動、画像撮影-------------------------------------------------------------------------------------------------------
    def manage_camera(self):
        print("manage_cameraモジュール（カメラ管理モジュール）が動作しました")
        
        # 静止画の読み込み（模擬動作）をコメントアウト
        #self.frame_oshidashi = cv2.imread("C:/startfile/g52024/image/oshidashi_image.jpg", 1)
        #self.frame_fukuro = cv2.imread("C:/startfile/g52024/image/fukuro_image.jpg", 1)
        #self.frame_qr = cv2.imread("C:/startfile/g52024/image/qr_image.jpg", 1)
        #self.frame_kensa1 = cv2.imread("C:/startfile/g52024/image/kensa1_image.jpg", 1)
        #self.frame_kensa2 = cv2.imread("C:/startfile/g52024/image/kensa2_image.jpg", 1)
        #self.frame_kensa3 = cv2.imread("C:/startfile/g52024/image/kensa3_image.jpg", 1)
        #self.frame_kensa4 = cv2.imread("C:/startfile/g52024/image/kensa4_image.jpg", 1)
        
        while(1):
            #time.sleep(0.1)
            #self.cap_oshidashi.set(cv2.CAP_PROP_EXPOSURE, -8)
            try:
                if self.is_camera_shutdown:
                    break
                
                ##各カメラから画像を取得 (Webカメラからのリアルタイム処理)
                ret1, self.frame_oshidashi = self.cap_oshidashi.read()
                ret2, self.frame_fukuro = self.cap_fukuro.read()
                ret3, self.frame_qr = self.cap_qr.read()
                ret4, self.frame_kensa1 = self.cap_kensa1.read()
                ret5, self.frame_kensa2 = self.cap_kensa2.read()
                ret6, self.frame_kensa3 = self.cap_kensa3.read()
                ret7, self.frame_kensa4 = self.cap_kensa4.read()
                if ret1 == False: # 最初のカメラが読み込めなければループを抜ける
                    break
                
                if(self.finish_cap_oshidashi): # 終了信号が来たらカメラを解放
                    self.cap_oshidashi.release()
                    self.cap_fukuro.release()
                    self.cap_qr.release()
                    self.cap_kensa1.release()
                    self.cap_kensa2.release()
                    self.cap_kensa3.release()
                    self.cap_kensa4.release()
                    cv2.destroyAllWindows()
                    time.sleep(5)

                # デバッグ表示（現在はコメントアウト）
                #cv2.imshow('oshidashi', self.frame_oshidashi)
                #cv2.imshow('fukuro', self.frame_fukuro)
                #cv2.imshow('qr', self.frame_qr)
                #cv2.imshow('左上', self.frame_kensa1)
                #cv2.imshow('右上', self.frame_kensa2)
                #cv2.imshow('左下', self.frame_kensa3)
                #cv2.imshow('右下', self.frame_kensa4)

                key = cv2.waitKey(1)
                
            #manage_cameraの例外処理
            except:
                self.datetime_now = datetime.datetime.now()#現在日時を取得
                self.datetime_now = self.datetime_now.isoformat()#日付データを文字列に変換
                #error_message = ":[Error] manage_camera, communication error with camera"#エラーメッセージを設定
                #response = requests.get(self.url + self.datetime_now + error_message)#エラーログ書込みプログラムを実行（GETで日付データとエラーメッセージを送信）
                #print (response.elapsed.total_seconds())
                import traceback
                traceback.print_exc()
                self.is_manage_camera_finish = True#画像撮影プログラム終了信号をTrueに
                print("画像撮影プログラム(while中の例外)でエラーが発生しました")
                time.sleep(5)

        print("manage_cameraモジュール（カメラ管理モジュール）を終了します")
        self.is_manage_camera_shutdown = True#シャットダウン信号をTrueに

        #カメラの接続不良が起こったら動作
        self.datetime_now = datetime.datetime.now()#現在日時を取得
        self.datetime_now = self.datetime_now.isoformat()#日付データを文字列に変換
        #error_message = ":[Error] manage_camera, communication error with camera"#エラーメッセージを設定
        #response = requests.get(self.url + self.datetime_now + error_message)#エラーログ書込みプログラムを実行（GETで日付データとエラーメッセージを送信）
        #print (response.elapsed.total_seconds())
        import traceback
        #traceback.print_exc()
        #self.is_manage_camera_finish = True#画像撮影プログラム終了信号をTrueに
        #print("画像撮影プログラムでエラーが発生しました")
        #time.sleep(5)
            
            
    ##手や身体の検出-------------------------------------------------------------------------------------------------------------
    def detect_hand(self):
        ##カメラが最初の画像を取得するまで待機
        time.sleep(5)
        print("detect_handモジュール（手検出モジュール）が動作しました")
        self.is_detect_hand = False
        #cv2.namedWindow('hands', cv2.WINDOW_NORMAL)
        mask = cv2.imread(self.mask_oshidashi_filepath, 1)
        with self.mp_hands.Hands(static_image_mode=True,
            max_num_hands=2, # 検出する手の数（最大2まで）
            min_detection_confidence=0.01) as hands:#検出精度をほぼ0に設定
            while(1):
                self.is_detect_hand = False
                try:
                    if self.is_camera_shutdown:
                        break

                    image = cv2.cvtColor(self.frame_oshidashi, cv2.COLOR_BGR2RGB)
                    imagea = cv2.cvtColor(self.frame_oshidashi, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False

                    image = cv2.bitwise_and(image, mask)

                    # 推論処理
                    hands_results = hands.process(image)

                    # 前処理の変換を戻しておく。
                    image.flags.writeable = True
                    write_image = cv2.cvtColor(imagea, cv2.COLOR_RGB2BGR)

                    #手が検出された場合、
                    if hands_results.multi_hand_landmarks:
                        for landmarks in hands_results.multi_hand_landmarks:
                            self.mp_drawing.draw_landmarks(
                                write_image,
                                landmarks,
                                self.mp_hands.HAND_CONNECTIONS,
                                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                self.mp_drawing_styles.get_default_hand_connections_style())

                        self.is_detect_hand = True
                    else:
                        self.is_detect_hand = False
                    
                    # ディスプレイ表示
                    #cv2.imshow('hands', write_image)

                    key = cv2.waitKey(1)


                except:
                    self.is_detect_hand = True
                    #print("予期せぬエラー（手判定）")

            print("detect_handモジュール（手検出モジュール）を終了します")
            self.is_detect_hand_shutdown = True#シャットダウン信号をTrueに
    
    
    ##画像処理の動作管理-------------------------------------------------------------------------------------------------------
    def manage_image_processing(self):
        ##カメラが最初の画像を取得するまで待機
        time.sleep(5)
        print("manage_image_processingモジュール（画像処理動作モジュール）が動作しました")
        #self.read_qr(self.frame_oshidashi)#ラベル貼りを動作する際にコメントアウト
        while(1):
            time.sleep(0.1)
            if self.is_camera_shutdown:
                break
            
            #ファイルアクセスを行うと0.1秒ほど時間がかかってしまう
            #各モジュールではデバッグのため画像を保存しているが、本番環境ではいらないかも
            #押出部の開始信号がTrueになったら動作
            if self.is_start_oshidashi:
                start = time.time()#時間測定開始
                
                self.judge_oshidashi(self.frame_oshidashi)#押出部のワーク有無判定モジュールの実行
                self.is_send_oshidashi_result = True#押出部終了信号をTrueに
                self.is_start_oshidashi = False#押出部開始信号をFalseに
                
                stop = time.time()#時間測定終了
                print("押し出し部の検査にかかった時間は")
                print(stop - start)
                print("-------------------------------------------------")
                
            #袋セット部の開始信号がTrueになったら動作
            if self.is_start_fukuro:
                start = time.time()#時間測定開始
                
                self.judge_fukuro(self.frame_fukuro)#袋セット部の袋有無判定モジュールの実行
                self.is_send_fukuro_result = True#袋セット部終了信号をTrueに
                self.is_start_fukuro = False#袋セット部開始信号をFlaseに
                
                stop = time.time()#時間測定終了
                print("袋セット部の検査にかかった時間は")
                print(stop - start)
                print("-------------------------------------------------")
                
            #検査部の開始信号がTrueになったら動作
            if self.is_start_kensa:
                start = time.time()#時間測定開始
                
                self.judge_kensa(self.frame_kensa1, self.output_kensa1_image_filepath, self.mask_kensa1_filepath)#検査部の袋穴あき検査モジュールの実行
                self.judge_kensa(self.frame_kensa2, self.output_kensa2_image_filepath, self.mask_kensa2_filepath)#検査部の袋穴あき検査モジュールの実行
                self.judge_kensa(self.frame_kensa3, self.output_kensa3_image_filepath, self.mask_kensa3_filepath)#検査部の袋穴あき検査モジュールの実行
                self.judge_kensa(self.frame_kensa4, self.output_kensa4_image_filepath, self.mask_kensa4_filepath)#検査部の袋穴あき検査モジュールの実行
                print(self.read_qr(self.frame_qr))#qr読取りモジュールの実行
                
                stop = time.time()#時間測定終了
                print("検査部の検査にかかった時間は")
                print(stop - start)
                print("-------------------------------------------------")
                
                self.is_send_kensa_result = True#検査部終了信号をTrueに
                self.is_start_kensa = False#検査部開始信号をFalseに

        print("manage_image_processingモジュール（画像処理動作モジュール）を終了します")
        self.is_manage_image_processing = True#シャットダウン信号をTrueに
    
    
    ##押出部のワーク有無判定------------------------------------------------------------------------------------------------------
    def judge_oshidashi(self, image):
        print("押出部のワーク有無判定")
        
        mask = cv2.imread(self.mask_oshidashi_filepath, 0)#押出部のマスク画像の読み込み
        #size = (1920, 1080)#画像サイズ
        size = (640, 480)#画像サイズ
        image = cv2.resize(image, size)#カメラ画像をリサイズ
        mask = cv2.resize(mask,size)#マスク画像をリサイズ
        image_size = image.shape[0] * image.shape[1]#画像サイズの面積を算出
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#画像をグレースケールに変換
        image = cv2.bitwise_and(image, mask)#マスク処理
        thresh_value, image_area = cv2.threshold(image, 89, 255, cv2.THRESH_BINARY)#2値化処理
        whitePixels = cv2.countNonZero(image_area)#白色の部分を算出
        blackPixels = image_size - whitePixels#黒色の部分を算出
    
        whiteAreaRatio = (whitePixels/image_size) * 100#白色の部分の割合を算出
        blackAreaRatio = (blackPixels/image_size) * 100#黒色の部分の割合を算出
    
        print("White Area [cm2] : ", whiteAreaRatio)
        print("Black Area [cm2] : ", blackAreaRatio)
        
        cv2.imwrite("image/oshidashi_result.jpg", image_area)#処理後画像を保存
        if whiteAreaRatio >= 24.45:
            self.oshidashi_result = 1#ワークセットOK
            print("ワークセットOK")
        else:
            self.oshidashi_result = 2#ワークセットNG
            print("ワークセットNG")
    
    
    ##袋セット部の袋の有無判定---------------------------------------------------------------------------------------------------
    def judge_fukuro(self, image):
        print("袋セット部の袋の有無判定")
        
        mask = cv2.imread(self.mask_fukuro_filepath, 0)#押出部のマスク画像の読み込み
        size = (640, 480)#画像サイズ
        image = cv2.resize(image, size)#カメラ画像をリサイズ
        mask = cv2.resize(mask,size)#マスク画像をリサイズ
        image_size = image.shape[0] * image.shape[1]#画像サイズの面積を算出
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#画像をグレースケールに変換
        image = cv2.bitwise_and(image, mask)#マスク処理
        thresh_value, image_area = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)#2値化処理
        whitePixels = cv2.countNonZero(image_area)#白色の部分を算出
        blackPixels = image_size - whitePixels#黒色の部分を算出
    
        whiteAreaRatio = (whitePixels/image_size) * 100#白色の部分の割合を算出
        blackAreaRatio = (blackPixels/image_size) * 100#黒色の部分の割合を算出
    
        print("White Area [cm2] : ", whiteAreaRatio)
        print("Black Area [cm2] : ", blackAreaRatio)
        
        #cv2.imwrite("image/fukuro_result.jpg", image_area)#処理後画像を保存
        
        if whiteAreaRatio >= 5:
            self.fukuro_result = 1#袋あり
            print("袋あり")
        else:
            self.fukuro_result = 2#袋なし
            print("袋なし")
        
        
    ##検査部の袋の破れ有無判定----------------------------------------------------------------------------------------------------
    def judge_kensa(self, image, path, mask_filepath):
        print("検査部の袋の破れ有無判定")
        
        #画像読み込み
        image_color = image#カメラのカラー画像
        mask = cv2.imread(mask_filepath, 0)#袋の角マスク画像
        hansya = cv2.imread(self.hansya_filepath, 0)#反射除去用のグレー画像
        
        #画像サイズの変更
        size = (640,480)#画像サイズ
        image = cv2.resize(image, size)
        image_color = cv2.resize(image_color, size)
        mask = cv2.resize(mask, size)
        hansya = cv2.resize(hansya, size)
        
        image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)#グレー画像に変換
        thresh_value, nitika_image = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY)#袋の反射部分を取得
        hihanten = nitika_image#袋の反射部分が白の画像
        hanten = 255 - nitika_image#袋の反射部分が黒の画像
        nitika_image = cv2.bitwise_and(image, hanten)#元画像に対して、袋の反射部分を切り取る
        hansya = cv2.bitwise_and(hansya, hihanten)#グレー画像を袋の反射に合わせて切り取る
        nitika_image = cv2.add(nitika_image, hansya)#反射部分をグレー画像に差し替え
        #cv2.imwrite("C:/startfile/g52024/image/hansya.jpg", nitika_image)#反射をなくした画像を表示
        
        image = nitika_image
        
        ##平滑化
        image = cv2.medianBlur(image, 5)
        image = cv2.medianBlur(image, 5)
        image = cv2.medianBlur(image, 5)

        ##2値化してエッジ処理
        th1 = 94
        th2 = 23
        nitika_image = cv2.Canny(image, th1, th2)#キャニー処理
        #cv2.imwrite("C:/startfile/g52024/image/canny.jpg", nitika_image)#反射をなくした画像を表示

        nitika_image = cv2.bitwise_and(nitika_image, mask)#マスク処理
        
        ##輪郭検出----------------------------------------------------------------------
        nitika_image_color = cv2.cvtColor(nitika_image,cv2.COLOR_GRAY2BGR)#グレー画像をカラー画像に変換
        #ret,thresh = cv2.threshold(nitika_image, 63, 255, cv2.THRESH_BINARY)#白黒のエリアを決定
        contours,hierarchy = cv2.findContours(nitika_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#輪郭を検出
        contimg = cv2.drawContours(nitika_image_color, contours, -1, (0, 255, 0), 7)#輪郭を書き込み
        
        ##穴あきを検出-----------------------------------------------------------------------------
        contimg_gray = cv2.cvtColor(contimg, cv2.COLOR_BGR2GRAY)#輪郭画像をグレー画像に変換
        thresh_value, image = cv2.threshold(contimg_gray, 100, 255, cv2.THRESH_BINARY)#輪郭部分を白色に
        nlabel, image_label = cv2.connectedComponents(image)#ラベリング処理
        #ラベリングされた部分を描画
        self.kensa_result = 1#破れなし(1)
        for i in range(1, nlabel):
            image_dst = cv2.compare(image_label, i, cv2.CMP_EQ)#元画像とラベリング画像を比較
            x, y, w, h = cv2.boundingRect(image_dst)#矩形領域を算出
            #ある程度大きい矩形を穴あきと判定
            if h >= 20:
                #cv2.rectangle(image_color, (x,y), (x+w, y+h), (0,0,240), 3)#穴あき部分を囲む
                self.kensa_result = 2#破れあり(2)
                print("穴あきあり")
        #cv2.imwrite("C:/startfile/g52024/image/image_color.jpg", image_color)#ラベリング画像を保存
        
        
        
    ##QRコード読み取り--------------------------------------------------------------------------------
    def read_qr(self, image):
        print("QRを読み取ります")
        #ser = serial.Serial("COM5", 9600) # ここのポート番号を変更
        #val = 100 # ここの値を変更すると、Arduinoの挙動が変わる
        #time.sleep(13)
        #return "1111, aaa, 111"
        #"""
        
        # QRCodeDetectorオブジェクトを作成する
        detector = cv2.QRCodeDetector()
        
        image = image[450:670,900:1120]
        image = cv2.resize(image, (400,400))
        
        cv2.imwrite("C:/startfile/g52024/image/image_qr.jpg", image)
        
        print("QRコード読取り")
        try:
            retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(image)
            
            ##QRコードの文字列を表示
            print(decoded_info[0])
            print("QR読取り完了")
            ##区切り文字指定
            dem = decoded_info[0].split(',')

            ##QRコードに意味のない半角スペースが入っているので除去
            ##QRコードの仕様を企業としっかり話し合う必要有
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
            
            #最終日に気付いたが、生産商品情報登録するプログラムを作るのを忘れていた
            #本来であればこの行に、QRコードから取得した情報をもとにデータベースに書込む処理を入れる
            
        
        except:
            import traceback
            traceback.print_exc()
        
        return#ラベル貼りを使用する際にコメントアウト（273行目も）
        #ラベル貼り装置自体はきちんと動作するが、通信などのエラー処理をしていないので自動運転に組み込むのはまだ怖い
        #最終プログラムではあるが、動作するか不安なので実行前にreturnしている
        #最後まで作りこみが甘いのは申し訳ないと思っている
        if self.is_start_ser:
            self.is_start_ser = False
            print("ラベル貼りと接続します")
            self.ser = serial.Serial("COM5", 9600)#ポート番号が違う場合はこの部分を変更する
            print("初期動作を終了します")
        elif self.is_ser_finish:
            pass
        else:
            print("動作開始")
            self.ser.write(bytes('1','utf-8'))
            print("送信完了")

            time.sleep(15)

            #while val_arduino != '2':
            #    try:
            #        val_arduino = self.ser.readline()
            #        print("2を受け取りました")
            #    except:
            #        print("例外")
                
            print("終了")
            self.is_ser_finish = True
            #self.ser.close()
        return