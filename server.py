import socketserver
import socket
import select
import threading

import wx

class windowClass(wx.Frame):
    def __init__(self, parent, title):
        super(windowClass, self).__init__(parent, title=title, size=(700, 600))

        self.panel = MyPanel(self)

class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.listbox = wx.ListBox(self)
        hbox.Add(self.listbox, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        btnPanel = wx.Panel(self)
        newBtn = wx.Button(btnPanel, wx.ID_ANY, 'New', size=(90, 30))
        delBtn = wx.Button(btnPanel, wx.ID_ANY, 'Delete User', size=(90,30))
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=delBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.NewItem,  id=newBtn.GetId())

        vbox.Add((-1, 20))
        vbox.Add(newBtn)
        vbox.Add(delBtn, 0, wx.TOP, 5)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        self.SetSizer(hbox)

        self.Centre()
    def OnDelete(self, event):
        sel = self.listbox.GetSelection()
        if sel != -1:
            self.listbox.Delete(sel)
    def NewItem(self, text):
        # text = wx.GetTextFromUser('Enter a new item', 'Insert dialog')
        self.listbox.Append(text)
            
app = wx.App()
# windowClass(None)
frame = windowClass(parent=None, title="List Box")
header_length = 10
Ip    = "10.49.56.129"
Port  = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


server_socket.bind((Ip, Port))
server_socket.listen()

sockets_list = [server_socket]
clients = {} # the clients list

def recv_message(client_socket):
    try:
        message_header = client_socket.recv(header_length)
        if not len(message_header):
            return False 
        message_length = int(message_header.decode('utf-8').strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False

def send_message(client_socket):
    ## send a message back to the user
    pass

def run_server():
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = recv_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = user

            frame.panel.NewItem("Accepted connection from {}:{} username:{}".format(client_address[0], client_address[1], user['data'].decode('utf-8')))
        else:
            message = recv_message(notified_socket)

            if message is False:
                frame.panel.NewItem("Closed connection from {}".format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            frame.panel.NewItem("Recieved message from {} : {}".format(user['data'].decode('UTF-8'), message['data'].decode('utf-8')))
            print("Recieved message from {} : {}".format(user['data'].decode('UTF-8'), message['data'].decode('utf-8')))

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:    
        sockets_list.remove(notified_socket) 
        del clients[notified_socket]     

server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

frame.Show()
app.MainLoop()

