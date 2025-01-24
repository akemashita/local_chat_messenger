import os
import socket
import json
from faker import Faker

fake = Faker("ja-JP")


def start_server():
    try:
        # ストリームのエンドポイントとなるソケットを作成する
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # サーバの UNIX ソケットの場所を設定する
        try:
            config = json.load(open("config.json"))
            server_address = config["filepath"]

        except FileNotFoundError:
            print("設定ファイル（config.json）が見つかりません。プログラムを終了します。")
            exit(1)

        # 以前の接続が残っていた場合に備えて、サーバアドレスを削除する（unlink）
        try:
            os.unlink(server_address)
        except FileNotFoundError:
            pass

        print("Starting up on {}".format(server_address))

        # サーバのアドレスにソケットを接続する（bind）
        sock.bind(server_address)

        # ソケットが接続要求を待機するようにする
        sock.listen(1)

        # クライアントからの接続を待ち続ける
        flag = True
        while flag:

            # クライアントからの接続を受け入れる
            connection, client_address = sock.accept()

            # client_address が空の場合の処理
            if not client_address:
                client_address = "Unix socket(no client address)"

            try:
                print("connection from: {}".format(client_address))

                message_to_client = (
                    "チャットを開始します。\nあなたの名前を教えてください。\n>> "
                )
                connection.sendall(message_to_client.encode())
                client_name = connection.recv(100).decode("utf-8")
                print("Received: " + client_name)

                message_to_client = "こんにちは {} さん。コマンドは help で見ることができます。\n>> ".format(
                    client_name
                )
                connection.sendall(message_to_client.encode())

                # クライアントからの新しいメッセージを待ち続ける
                talk_flag = False
                while True:
                    # 接続からデータを読み込む（最大16byte)
                    data = connection.recv(100)

                    # 受け取ったデータを文字列に変換する
                    data_str = data.decode("utf-8")

                    # 受け取ったデータを表示する
                    print("Received: " + data_str)

                    # データがあれば次の処理を行う
                    if data:
                        response = chat_bot(data_str)

                        # 処理したメッセージをバイナリ形式に変換してクライアントに送り返す
                        connection.sendall(response.encode())

                        # exit コマンドを受け取った場合はループから抜ける
                        if data_str == 'exit':
                            print('Closing connection for: {}'.format(client_address))
                            flag = False
                            break

                    else:
                        print("no data from: {}".format(client_address))
                        break

            # 最終的に接続を閉じる
            finally:
                print("Closing current connection")
                connection.close()

    except Exception as e:
        print(f'エラーが発生しました: {e}')
        connection.close()


def str_to_integer(str_input):
    try:
        return int(str_input)
    except:
        return 0


def chat_bot(client_input):
    # クライアントからの入力を受け取る
    client_message = client_input.strip().lower()

    if client_message == "exit":
        return "チャットを終了します。さようなら！\n"

    elif client_message == "help":
        return "name <整数値>: 名前を<整数値>の数だけ生成します。（上限50）\nphone <整数値>: 電話番号を<整数値>の数だけ生成します。（上限50）\naddress <整数値>: 住所を<整数値>の数だけ生成します。\nsent:文をランダムに生成します。\nbot: ボットの名前を表示します。\nhello: 挨拶をします。\n>> "

    elif client_message == "bot":
        fake_name = fake.name()
        return "私は {} です！\n>> ".format(fake_name)

    elif client_message.split()[0] == "name":
        if len(client_message.split()) >= 2:
            num = str_to_integer(client_message.split()[1])
            if isinstance(num, int) and num > 0 and num <= 50:
                fake_names = ""
                for _ in range(num):
                    fake_names += fake.name() + "\n"
                print(fake_names)
                return fake_names + "\n名前の生成が終わりました。\n>> "
            else:
                return "引数に誤りがあります。1-50 を入力してください。（例： name 3）\n>> "
        else:
            return "コマンド name には 1-50 の引数が必要です。（例： name 3）\n>> "

    elif client_message.split()[0] == "phone":
        if len(client_message.split()) >= 2:
            num = str_to_integer(client_message.split()[1])
            if isinstance(num, int) and num > 0 and num <= 50:
                fake_phones = ""
                for _ in range(num):
                    fake_phones += fake.phone_number() + "\n"
                print(fake_phones)
                return fake_phones + "\n電話番号の生成が終わりました。\n>> "
            else:
                return "引数に誤りがあります。1-50 を入力してください。（例： phone 3）\n>> "
        else:
            return "コマンド phone には 1-50 の引数が必要です。（例： phone 3）\n>> "

    elif client_message.split()[0] == "address":
        if len(client_message.split()) >= 2:
            num = str_to_integer(client_message.split()[1])
            if isinstance(num, int) and num > 0 and num <= 50:
                fake_addresses = ""
                for _ in range(num):
                    fake_addresses += fake.address() + "\n"
                print(fake_addresses)
                return fake_addresses + "\n住所の生成が終わりました。\n>> "
            else:
                return "引数に誤りがあります。1-50 を入力してください。（例： phone 3）\n>> "
        else:
            return "コマンド phone には 1-50 の引数が必要です。（例： phone 3）\n>> "

    elif "hello" in client_message or "こんにちは" in client_message:
        return "こんにちは！今日はどんなことをお手伝いしましょうか？\n>> "

    elif client_message == "sent":
        return fake.paragraph() + "\n>> "

    else:
        return "ごめんなさい。そのコマンド {} には対応していません。\n>> ".format(
            client_message
        )


if __name__ == "__main__":
        start_server()
        exit(0)