from tkinter import *
import socket
import threading
from time import sleep
from tkinter import messagebox

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                lst.insert(END, "Server: Kết nối đã đóng.")
                break
            lst.insert(END, "Chủ Quán: " + message)
        except ConnectionResetError:
            lst.insert(END, "Server: Kết nối đã đóng.")
            break

# def calculate_bill():
#     total_price = sum(item_prices)
#     return total_price

def update_total_price():
    # Tính lại tổng tiền dựa trên giá của từng món hàng và số lượng
    total_price = sum(item_prices)
    # tổng tiền
    return total_price


def bill_order(lst_order):
    # Khởi tạo chuỗi kết quả
    result = ""
    for item in lst_order:
        # Thêm tên món ăn vào chuỗi kết quả
        result += item + ", "
    # Loại bỏ dấu phẩy cuối cùng và khoảng trắng
    result = result.rstrip(", ")
    # Trả về chuỗi kết quả
    return result

# def update_bill_list():
#     bill_list.delete(0, END)
#     for item in selected_items:
#         bill_list.insert(END, item)
def update_bill_list():
    bill_list.delete(0, END)
    # Thêm mỗi món hàng và số lượng vào danh sách hiển thị
    for item, quantity in selected_itemsx.items():
        bill_list.insert(END, f"{item} x{quantity}")

selected_itemsx = {}
# lst_order1 = []
def creOrder(menu_item):
    message = menu_item[2:]
    message = f"order  {message}"
    # Lấy giá của món hàng
    price = int(message.split("Giá: ")[1].split(" VND")[0])
    item_name = str(message)
    # # Lấy ten của món hàng để so sánh, thêm vào dictionary khác
    # lst_order1.append(str(message.split("order")[1].split(" Giá")[0]))
    # print(lst_order1)
    selected_items.append(message)
    # Kiểm tra xem món hàng đã tồn tại trong danh sách chưa
    if item_name in selected_itemsx:
        # Nếu đã tồn tại, tăng số lượng lên 1
        selected_itemsx[item_name] += 1
    else:
        # Nếu chưa tồn tại, thêm món hàng vào danh sách với số lượng là 1
        selected_itemsx[item_name] = 1
    # Lưu giá của món hàng đã chọn vào danh sách
    item_prices.append(price)
    lst_order.append(item_name)
    #update bill order hien thi len lst2
    update_bill_list()
    money = update_total_price()
    tongTien.config(text=f'Total: {money} ')

def connect_to_server():
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('127.0.0.10', 10000)
        client_socket.connect(server_address)
        threading.Thread(target=receive_messages).start()
    except:
        print("không kết nối được máy chủ")

def send_message():
    message3 = entry.get()
    lst.insert(END, "You: " + message3)
    entry.delete(0, END)
    if client_socket:
        try:
            client_socket.send(("***"+ message3).encode())
        except OSError:
            lst.insert(END, "Kết nối đã đóng, không thể gửi tin nhắn.")

def send_order_to_server():
    if client_socket:
        try:
            check = messagebox.askyesno("Xác nhận","Bạn chắc chắn muốn gửi?")
            if(check == True):
                # Chuyển danh sách selected_items thành chuỗi
                order_message = "\n".join(selected_items)

                # lstorder = bill_order(lst_order)
                print(order_message)
                money = update_total_price()
                # Tính số loại vật phẩm đã order, không tính vật phẩm trùng
                num_unique_items = len(set(selected_itemsx))
                lst.insert(END, f"Bạn đã yêu cầu đơn hàng gồm {num_unique_items} loại vật phẩm:")
                for item, quantity in selected_itemsx.items():
                    lst.insert(END, f"{item} x{quantity} đơn")

                lst.insert(END, f"Tổng bill: {money}")
                # Gửi chuỗi đến server
                client_socket.send(order_message.encode())
                lst.insert(END, "đến máy chủ.")
                # Clear the order lists after sending
                selected_items.clear()
                selected_itemsx.clear()
                lst_order.clear()
                # lst_order1.clear()
                item_prices.clear()
                bill_list.delete(0, END)
            else:
                messagebox.showinfo("Thông báo","Chưa được gửi!")
        except OSError:
            lst.insert(END, "Kết nối đã đóng, không thể gửi đơn hàng.")


def delete_items():
    try:
        # Lấy tên của món hàng cuối cùng đã order
        last_item = selected_items[-1]
        # Xóa phần tử cuối cùng từ selected_itemsx và lấy key và value của phần tử đó
        # Giảm số lượng của món hàng cuối cùng từ selected_itemsx
        selected_itemsx[last_item] -= 1
        # Nếu số lượng món hàng đã giảm xuống 0, xóa món hàng đó khỏi selected_itemsx
        if selected_itemsx[last_item] == 0:
            del selected_itemsx[last_item]
        print("dic order",selected_itemsx)

        # Xóa dữ liệu trong item_prices và cập nhật lại
        item_prices.pop()
        # Nếu không còn món hàng cuối cùng, xóa hết dữ liệu trong selected_items
        if len(selected_items) == 1:
            selected_items.clear()
        else:
            selected_items.pop()
        print("list order",selected_items)
        update_bill_list()
        # Tính lại tổng giá tiền
        money = update_total_price()
        tongTien.config(text=f'Total: {money} ')
    except KeyError:
        print("Không còn dữ liệu để xóa!")


def handle_exit():
    # Đóng kết nối với máy chủ trước khi thoát
    if client_socket:
        client_socket.close()
    win.destroy()
    win.quit()


win = Tk()
win.title("Máy số 1")
win.minsize(height=400, width=700)

lst = Listbox(win, width=70, height=10)
lst.place(x=250, y=0)

entry = Entry(win, width=45, font='Arial')
entry.place(x=250, y=180)

btn = Button(win, width=16, height=2, text="Gửi Tin Nhắn", bg="#8ddad5",fg='white')
btn_order = Button(win, width=16, height=2, text="Order", bg="#8ddad5",fg='white')
btn_xoa = Button(win, width=16, height=2, text="Xóa Danh Sách Order", bg="#8ddad5",fg='white',command=delete_items)


btn.place(x=340, y=230)
btn_order.place(x=250, y=550)
btn_xoa.place(x=440, y=550)

btn.config(command=send_message)

# Danh sách lưu giá tiền của mỗi món hàng đã chọn
item_prices = []
# Danh sách lưu món hàng đã chọn
selected_items = []
lst_order = []
# Tạo listbox để hiển thị danh sách tính tiền
bill_list = Listbox(win, width=70, height=10)
bill_list.place(x=250,y=300)

# Thay đổi text của button "Order" thành "Send Order" và gán command là send_order_to_server
btn_order = Button(win, width=16, height=2, text="Send Order", bg="#8ddad5", fg='white', command=send_order_to_server)
btn_order.place(x=250, y=550)


images = ["noodle.png", "coca.png", "bread.png", "redbull.png", "snack.png"]
names = [
    "1.Mỳ Tôm Trứng \nGiá: 15000 VND\n",
    "2.Coca Cola Japan \nGiá: 25000 VND\n",
    "3.Bánh mỳ Đan Mạch \nGiá: 25000 VND\n",
    "4.Bò Húc \nGiá: 15000 VND\n",
    "5.Snack Khoai Tây \nGiá: 10000 VND\n"
]
names1 = [
    "1.Mỳ Tôm Trứng Giá: 15000 VND ",
    "2.Coca Cola Japan Giá: 25000 VND ",
    "3.Bánh mỳ Đan Mạch Giá: 25000 VND ",
    "4.Bò Húc Giá: 15000 VND ",
    "5.Snack Khoai Tây Giá: 10000 VND "
]
i = 2
j = 0
images_list = []
# Tính toán và cập nhật danh sách tính tiền khi có món hàng được chọn
for img, name, name1 in zip(images, names, names1):
    imag = PhotoImage(file=img)
    images_list.append(imag)
    menu_item = name
    menu_item1 = name1
    noodle = Button(win, image=imag, command=lambda menu_item1=menu_item1: creOrder(menu_item1))
    noodle2 = Label(win, text=name)
    noodle.grid(row=i - 1, column=0)
    noodle2.grid(row=i, column=0)
    i += 2
    j += 1

images1 = ["comRang.png", "bunBo.png", "pepsi.png", "coffee.png", "orange.png"]
names2 = [
    "6.Cơm rang \nGiá: 35000 VND\n",
    "7.Bún Bò \nGiá: 30000 VND\n",
    "8.Pepsi\nGiá: 15000 VND\n",
    "9.Coffee\nGiá: 20000 VND\n",
    "10Nước Cam\nGiá: 20000 VND\n"
]
names3 = [
    "6.Cơm rang Giá: 35000 VND ",
    "7.Bún Bò Giá: 30000 VND ",
    "8.Pepsi Giá: 15000 VND ",
    "9.Coffee Giá: 20000 VND ",
    "10Nước Cam Giá: 20000 VND "
]
a = 2
b = 0
images_list1 = []
# Tính toán và cập nhật danh sách tính tiền khi có món hàng được chọn
for img1, name2, name3 in zip(images1, names2, names3):
    imag1 = PhotoImage(file=img1)
    images_list1.append(imag1)
    menu_item2 = name2
    menu_item3 = name3
    noodle = Button(win, image=imag1, command=lambda menu_item3=menu_item3: creOrder(menu_item3))
    noodle2 = Label(win, text=name2)
    noodle.grid(row=a - 1, column=1)
    noodle2.grid(row=a, column=1)
    a += 2
    b += 1
# Tạo label để hiển thị tổng tiền
tongTien = Label(win,fg='red',text=f'Total: 0 ',width=10,height=1)
tongTien.place(x= 250,y=490)
# Kết nối đến máy chủ
connect_to_server()

# Thêm chức năng xử lý khi đóng cửa sổ
win.protocol("WM_DELETE_WINDOW", handle_exit)

# Khởi chạy vòng lặp chính của ứng dụng
win.mainloop()

