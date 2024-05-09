from datetime import datetime
from tkinter import Tk, Listbox, Button, Entry, END, Scrollbar, SINGLE, Label
import tkinter.font as font
import socket
import threading

# Function to send message to client
def send_message():
    message = input.get()
    selected_index = lst_clients.curselection()  # Get the index of the selected client
    if selected_index:  # Check if any client is selected
        client_socket = client_sockets[selected_index[0]]  # Get the selected client socket
        client_socket.send(message.encode())
        lstms.insert(END, "You to {}: {}".format(lst_clients.get(selected_index), message))
    else:
        lstms.insert(END, "You: " + message)
        for client_socket in client_sockets:
            client_socket.send(message.encode())
    input.delete(0, END)

def update_clients_list():
    lst_clients.delete(0, END)
    for client_socket in client_sockets:
        # lst_clients.insert(END, client_socket.getpeername()[0])
        client_address = client_socket.getpeername()
        client_info = f"{client_address[0]}:{client_address[1]}"
        lst_clients.insert(END, client_info)
    print(client_sockets)

def receive_messages(client_socket, address):
    while True:
        try:
            message = client_socket.recv(4096).decode()
            # Khởi tạo từ điển để lưu trữ số lượng của mỗi mặt hàng
            item_quantity = {}
            total_price = 0
            if "***" in message:
                lstms.insert(END,"Máy {}: {}".format(client_sockets.index(client_socket) + 1, message.replace("***", "")))
            else:
                orders = message.split('\n')
                lst.insert(END, "Máy {}: Order \t\t\t\t\t{}".format(client_sockets.index(client_socket) + 1,str(datetime.now())))

                for order in orders:
                    # Tách tên mặt hàng và giá
                    item_name, price_str = order.split("Giá: ")
                    print(item_name)
                    price = int(price_str.split(" VND")[0])
                    print(price)

                    # Tăng số lượng tương ứng của mặt hàng trong từ điển
                    if item_name in item_quantity:
                        # Nếu đã tồn tại, tăng số lượng
                        item_quantity[item_name] += 1
                    else:
                        # Nếu chưa tồn tại, thêm mặt hàng mới vào từ điển với số lượng là 1
                        item_quantity[item_name] = 1

                    # Hiển thị mặt hàng và giá trị
                    # lst.insert(END, order)
                    total_price += price
                #hiển thị số loại vật phẩm
                num_unique_items = len(set(item_quantity))
                lst.insert(END, f"Máy {client_sockets.index(client_socket) + 1} đã yêu cầu đơn hàng gồm {num_unique_items} loại vật phẩm:")
                # Hiển thị số lượng của các mặt hàng
                for item_name, quantity in item_quantity.items():

                    item_name = str(item_name).replace("order","")
                    lst.insert(END, f"{item_name}: {quantity} đơn")

                lst.insert(END, f"Total bill: {total_price} VND")
                lst.insert(END, "\r\n")
        except ConnectionResetError:
            print("Connection reset by peer")
            client_sockets.remove(client_socket)
            update_clients_list()
            break
        except:
            print("An error occurred!")
            break

# Function to handle client connections
def handle_connections(server_socket):
    while True:
        server_socket.listen()
        connect, adr = server_socket.accept()
        client_sockets.append(connect)
        update_clients_list()
        threading.Thread(target=receive_messages, args=(connect, adr)).start()

# Function to initialize socket connection
def connect_to_server():
    global server_socket
    serverIP = '127.0.0.10'  # Change this to your server IP address
    severPort = 10000        # Change this to your server port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((serverIP, severPort))
    threading.Thread(target=handle_connections, args=(server_socket,)).start()
def handle_exit():
    # Đóng kết nối với máy chủ trước khi thoát
    if server_socket:
        server_socket.close()
    win.destroy()
    win.quit()
# Tkinter GUI setup
win = Tk()
win.title("Ứng Dụng Order Đồ Ăn Trong Quán Net")
win.minsize(height=500, width=980)

#order
lst = Listbox(win, width=80, height=23)
lst.grid(row=1, column=0)
scrollbar = Scrollbar(win, orient='vertical', command=lst.yview)
scrollbar.grid(row=1, column=1, sticky='ns')
lst.config(yscrollcommand=scrollbar.set)

#tin nhan
lstms = Listbox(win, width=50, height=23)
lstms.grid(row=1, column=2)
scrollbar1 = Scrollbar(win, orient='vertical', command=lstms.yview)
scrollbar1.grid(row=1, column=3, sticky='ns')
lstms.config(yscrollcommand=scrollbar1.set)

lstmslb = Label(win, text = "Tin nhan gui tu client")
lstmslb.grid(row=2, column=2)

lst_clients = Listbox(win, width=25, height=23, selectmode=SINGLE)
lst_clients.grid(row=1, column=4)

input = Entry(win, width=38, font='Arial')
input.grid(row=2, column=0)

btnSend = Button(win, width=15, height=2, text="Gui tin nhan", background="#8ddad5",fg='white', command=send_message)
btnSend.grid(row=3, column=0)


client_sockets = []

connect_to_server()
win.protocol("WM_DELETE_WINDOW", handle_exit)
win.mainloop()
