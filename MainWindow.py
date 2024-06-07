from PySide6.QtCore import QThread, Signal, Slot, Qt, QElapsedTimer
from PySide6.QtWidgets import QApplication, QMainWindow
from GUI import Ui_MainWindow
import paho.mqtt.client as mqtt
import time
import matplotlib.pyplot as plt
questions = ["貓", "狗", "牛", "山羊", "豬", "鳥", "魚"]
answers = ["cat", "dog", "cow", "goat", "pig", "bird", "fish"]
# questions = ["貓", "卯"]
# answers = ["cat", "tac"]
scanned =[]
current_question = 0
elapsed_times = []


class MQTTClientThread(QThread):
    message_received = Signal(str)

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("Letter")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        print(message)
        self.message_received.emit(message)

    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("192.168.50.175", 1883, 60)
        self.client.loop_forever()


class HBMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.mqtt_thread = MQTTClientThread()
        self.mqtt_thread.message_received.connect(self.update_label)
        self.mqtt_thread.start()
        self.ui.question.setText(questions[0])
        self.ui.question.setAlignment(Qt.AlignCenter)
        self.ui.answer.setAlignment(Qt.AlignCenter)
        self.ui.messagebox.hide()
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()

    @Slot(str)
    def update_label(self, message):
        global scanned
        global current_question
        global elapsed_times
        if message == "+":
            #把scanned跟答案比對
            if ''.join(scanned) == answers[current_question]:
                if elapsed_times:
                    elapsed_times.append(self.elapsed_timer.elapsed() / 1000 - sum(elapsed_times))
                else:
                    elapsed_times = [self.elapsed_timer.elapsed() / 1000]
                self.ui.messagebox.setText("Correct!!")
                self.ui.messagebox.setAlignment(Qt.AlignCenter)
                self.ui.messagebox.show()
                current_question += 1
                self.ui.answer.setText("")
                scanned = []
                if current_question < len(questions):
                    self.ui.question.setText(questions[current_question])
                    self.ui.question.setAlignment(Qt.AlignCenter)
                else:
                    self.ui.question.setText("Finished in")
                    self.ui.question.setAlignment(Qt.AlignCenter)
                    self.finish_quiz()
                return
            else:
                self.ui.messagebox.setText("Incorrect!!")
                self.ui.messagebox.setAlignment(Qt.AlignCenter)
                self.ui.messagebox.show()
                return
        elif message == "-":
            if scanned:
                scanned.pop()
        else:
            #把message改成小寫
            message = message.lower()
            scanned.append(message)
        # 將scanned轉換成字串
        scannedtoshow = ''.join(scanned)
        self.ui.answer.setText(scannedtoshow)
        self.ui.answer.setAlignment(Qt.AlignCenter)
        self.ui.messagebox.hide()

    def finish_quiz(self):
        elapsed_time = self.elapsed_timer.elapsed() / 1000  # Convert milliseconds to seconds
        self.ui.answer.setText(f"{elapsed_time} s!")
        self.ui.answer.setAlignment(Qt.AlignCenter)
        print(f"Time taken: {elapsed_time} seconds")
        print(f"Time taken for each question: {elapsed_times}")
        self.plot_bar_chart(elapsed_times)

    def plot_bar_chart(self, elapsed_times):
        plt.bar(range(1, len(elapsed_times) + 1), elapsed_times)
        plt.xlabel('Question')
        plt.ylabel('Time (seconds)')
        plt.title('Time Taken for Each Question')
        plt.xticks(range(1, len(elapsed_times) + 1))  # Set x-axis ticks to integers
        plt.show()


if __name__ == '__main__':
    app = QApplication([])
    hb_window = HBMainWindow()
    hb_window.show()
    app.exec()
