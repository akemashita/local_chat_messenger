import socket
import sys
import os
import json

# ストリームのエンドポイントとなるソケットを作成する
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# サーバの UNIX ソケットの場所を設定する
try:
    config = json.load(open("config.json"))
    server_address = config["filepath"]

except FileNotFoundError:
    print("設定ファイル（config.json）が見つかりません。プログラムを終了します。")
    exit(1)


# server_address = "/tmp/socket_file"
print("connecting to server: {}".format(server_address))

# サーバに接続を行う
try:
    sock.connect(server_address)

# エラーが発生した場合は、プログラムを終了する
except socket.error as err:
    print("エラーが発生したため、プログラムを終了します: {}".format(err))
    sys.exit(1)

# サーバに正常に接続できたら、サーバにメッセージを送信する
try:
    message_from_server = sock.recv(200).decode("utf-8")
    message_str = input(message_from_server)

    # 入力メッセージを byte 型に変換する
    message = message_str.encode("utf-8")
    sock.sendall(message)

    sock.settimeout(2)

    try:
        while True:
            # サーバからデータを受け取る（最大は200byte）
            data = sock.recv(4096).decode("utf-8")

            # データがあれば表示して、なければ終了します。
            if data:
                # 前回の入力が exit であれば、サーバからのメッセージを表示して終了する
                if message_str == "exit":
                    print(data)
                    break

                else:
                    while True:
                        message_str = input(data)

                        if len(message_str) > 0:
                            message = message_str.encode("utf-8")
                            sock.sendall(message)
                            break

            else:
                break

    except TimeoutError:
        print("Socket timeout, ending listening for server messages")

finally:
    print("closing socket")
    sock.close()
