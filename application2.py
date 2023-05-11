import argparse
from socket import *
import headers
import threading
import sys
import os
import time

parser = argparse.ArgumentParser(description="TCP connection that can run in server and client mode")

parser.add_argument('-s', '--server', action='store_true')
parser.add_argument('-c', '--client', action='store_true')
parser.add_argument('-b', '--bind', type=str)
parser.add_argument('-p', '--port', type=int)
parser.add_argument('-r', '--reliable_method', type=str, choices=['stop_and_wait','GBN','SR'], default = 'stop_and_wait')
parser.add_argument('-f', '--file', type=str)
parser.add_argument('-t', '--test_case', type=str, choices=["none","loss","skip_ack"], default="none")


args = parser.parse_args()

header_format = '!IIHH'
buffer = 1472
buffer1 = 1484

def stop_and_wait():
    if args.server:
        acknum = 1
        addr = (args.bind, args.port)
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind((args.bind, args.port))
        f = open("test2.png", "wb")
        data, addr = serverSocket.recvfrom(buffer1)
        header_msg = data[:12]
        seq, ack, flags, win  = headers.parse_header(header_msg)
        syn, ack, fin = headers.parse_flags(flags)
        i = 0
        if(syn > 0):
            seq = 1
            flags = 12
            SynAckPackage = headers.create_packet(seq, ack, flags, 0, b'')
            serverSocket.sendto(SynAckPackage, addr)
            if(serverSocket.recvfrom(buffer1)):
                print("successfully established connection")
                start_time = time.time()
                while True:
                    data, addr = serverSocket.recvfrom(buffer1)
                    elapsed_time = time.time() - start_time
                    print("Receiving data...")
                    total_data =+ len(data)
                    message_body = data[12:]
                    seq, ack, flags, win = headers.parse_header(data[:12])
                    syn, ack , fin = headers.parse_flags(flags)
                    if(fin > 0):
                        flags = 4
                        data = headers.create_packet(seq, ack, flags, 0, b'')
                        f.close()
                        serverSocket.sendto(data, addr)
                        serverSocket.close()
                        print("Shutting down server...")
                        print("Mbps", total_data / elapsed_time / 8)
                        sys.exit()
                    else:
                        if args.test_case == "skip_ack":
                            i+=1
                            if i == 3:
                                continue
                            f.write(message_body)
                            flags=4
                            AckMessage = headers.create_packet(seq, ack, flags, 0, b'')
                            serverSocket.sendto(AckMessage, addr)
                        else:
                            f.write(message_body)
                            flags=4
                            AckMessage = headers.create_packet(seq, ack, flags, 0, b'')
                            serverSocket.sendto(AckMessage, addr)
    if args.client:
        addr = (args.bind, args.port)
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.connect((args.bind, args.port))
        client_socket.settimeout(2)
        f = open(args.file, "rb")
        filedata = f.read(buffer)
        #print(filedata)
        seq = 1
        acknum = 0
        flags = 8
        synpack = headers.create_packet(0,acknum,flags,0, b'')
        receiveSynAck= ""
        while True:
            client_socket.sendto(synpack, addr)
            try:
                receiveSynAck = client_socket.recv(1472)
                break
            except timeout:
                continue
        headersAck = receiveSynAck[:12]
        seq, ack, flags, win = headers.parse_header(headersAck)
        syn, ack, fin = headers.parse_flags(flags)
        if(syn>0 and ack> 0):
            seq = 0
            ack = 1
            flags = 4
            sendAck = headers.create_packet(seq,ack, flags,0,b'') 
            if(client_socket.sendto(sendAck, addr)):
                print("connection successfully established")
                while filedata:
                    message = headers.create_packet(seq,ack,flags,0,filedata)
                    while True:
                        try:
                            client_socket.sendto(message, addr)
                            serverAck = client_socket.recv(buffer1)
                            sSeq, sAck, sFlags, sWin  = headers.parse_header(serverAck[:12])
                            print(f"seq={sSeq}, sAck={sAck}, sFlags={sFlags}")
                            break
                        except timeout:
                            continue
                    filedata = f.read(buffer)
                flags = 2 
                finMsg = headers.create_packet(seq, ack,flags,0, b'')
                while True:
                    try:
                        client_socket.sendto(finMsg, addr)
                        if(client_socket.recv(buffer)):
                            print("closing connection...")
                            client_socket.close()
                            f.close()
                        break
                    except timeout:
                        continue


def SR():
    if args.server:
        acknum = 1
        addr = (args.bind, args.port)
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind((args.bind, args.port))
        f = open("test2.png", "wb")
        data, addr = serverSocket.recvfrom(buffer1)
        header_msg = data[:12]
        seq, ack, flags, win  = headers.parse_header(header_msg)
        syn, ack, fin = headers.parse_flags(flags)
        i = 0
        if(syn > 0):
            seq = 0
            flags = 12
            SynAckPackage = headers.create_packet(seq, ack, flags, 0, b'')
            serverSocket.sendto(SynAckPackage, addr)
            if(serverSocket.recvfrom(buffer1)):
                print("successfully established connection")
                while True:
                    data, addr = serverSocket.recvfrom(buffer1)
                    expAck, ack, flags, win = headers.parse_headers(data[:12])
                    if seq == expAck:
                        f.write(data[12:])


       
    if args.client:
        addr = (args.bind, args.port)
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.connect((args.bind, args.port))
        client_socket.settimeout(2)
        f = open(args.file, "rb")
        filedata = f.read(buffer)
        #print(filedata)
        seq = 1
        acknum = 0
        flags = 8
        synpack = headers.create_packet(0,acknum,flags,0, b'')
        receiveSynAck= ""
        while True:
            client_socket.sendto(synpack, addr)
            try:
                receiveSynAck = client_socket.recv(1472)
                break
            except Timeout:
                continue
        headersAck = receiveSynAck[:12]
        seq, ack, flags, win = headers.parse_header(headersAck)
        syn, ack, fin = headers.parse_flags(flags)
        if(syn>0 and ack> 0):
            seq = 0
            ack = 1
            flags = 4
            sendAck = headers.create_packet(seq,ack, flags,0,b'')
            if(client_socket.sendto(sendAck, addr)):
                print("connection successfully established")


def wait_for_ack(connection):
    connection.settimeout(2)
    ack = connection.recv(buffer)
    header = ack[:12]
    seq, ack , flags, win = headers.parse_header(header)
    print(f'seq={seq}, ack={ack},flags={flags}, win={win}')
    return ack, seq


def GBN():
    Window = 2
    if args.server:
        acknum = 0
        addr = (args.bind, args.port)
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind((args.bind, args.port))
        f = open("test2.png", "wb")
        data, addr = serverSocket.recvfrom(buffer1)
        header_msg = data[:12]
        seq, ack, flags, win  = headers.parse_header(header_msg)
        syn, ack, fin = headers.parse_flags(flags)
        i = 0
        if(syn > 0):
            seq = 0
            ack = 0
            flags = 12
            SynAckPackage = headers.create_packet(seq, ack, flags, 0, b'')
            serverSocket.sendto(SynAckPackage, addr)
            if(serverSocket.recvfrom(buffer1)):
                print("successfully established connection")
                start_time = time.time()
                elapsed = 0
                total_size = 0
                while True:
                    data, addr = serverSocket.recvfrom(buffer1)
                    print("Receiving data...")
                    message_body = data[12:]
                    recvSeq, ack, flags, win = headers.parse_header(data[:12])
                    print(f'seq={seq}, ack={ack}')
                    syn, ackflag, fin = headers.parse_flags(flags)
                    if(fin > 0):
                        flags = 4
                        data = headers.create_packet(seq, ack, flags, 0, b'')
                        f.close()
                        serverSocket.sendto(data, addr)
                        serverSocket.close()
                        print("Shutting down server...")
                        print("Mbps: ", total_size / elapsed_time / 8 )
                        sys.exit()
                    else:
                        if recvSeq == seq:
                            total_size += len(data)
                            elapsed_time = time.time() - start_time
                            print(len(message_body))
                            print(message_body)
                            f.write(message_body)
                            flags=0
                            print(f'seq={seq}, ack={ack}, win={win}')
                            AckMessage = headers.create_packet(seq, ack, flags, 0, b'')
                            serverSocket.sendto(AckMessage, addr)
                            seq+=1
                        else:
                            continue



    if args.client:
        read_files = []
        count = 0
        addr = (args.bind, args.port)
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.connect((args.bind, args.port))
        client_socket.settimeout(2)
        f = open(args.file, "rb")
        filedata = f.read(buffer)
        #print(filedata)
        seq = 1
        acknum = 0
        flags = 8
        synpack = headers.create_packet(0,acknum,flags,0, b'')
        receiveSynAck= ""
        while True:
            client_socket.sendto(synpack, addr)
            try:
                receiveSynAck = client_socket.recv(1472)
                break
            except timeout:
                continue
        headersAck = receiveSynAck[:12]
        seq, ack, flags, win = headers.parse_header(headersAck)
        syn, ack, fin = headers.parse_flags(flags)
        if(syn>0 and ack> 0):
            seq = 0
            ack = 0
            flags = 4
            sendAck = headers.create_packet(seq,ack, flags,0,b'')
            if(client_socket.sendto(sendAck, addr)):
                print("connection successfully established")
                window_start = 0
                window_size = 5
                window_end = min(window_start + window_size, len(read_files))
                while filedata:
                    read_files.append(filedata)
                    print("added data to array of lenght,", len(filedata))
                    filedata = f.read(buffer)
                print(len(read_files))
                print(sys.getsizeof(filedata))
                for i in range(0, len(read_files)):
                    print(read_files[i])
                while window_start < len(read_files)-1:
                    window_end = min(window_start + window_size, len(read_files))
                    for i in range(window_start, window_end):
                        message_data = headers.create_packet(i, ack, flags, 0, read_files[i])
                        print(seq)
                        #print(f'seq={seq}, ack={ack}, win={win}')
                        client_socket.sendto(message_data, addr)
                        seq+=1
                    try:
                        data, addr = client_socket.recvfrom(buffer)
                        seq, ack, flags, win  = headers.parse_header(data)
                        if ack is None:
                            print("no ack aquired")
                            window_start = window_start
                            window_end = min(window_start + window_end, len(read_files)-1)
                        elif seq>= window_start:
                            print("ack aquired")
                            print("current",seq)
                            window_start=seq+1
                            print("window start", window_start)
                            window_end = min(window_start + window_size, len(read_files)-1)
                        else:
                            print("something went wrong")
                    except timeout:
                        window_end = window_start + window_size
                
                flags = 2
                finPackage = headers.create_packet(seq,ack,flags,0, b'')
                client_socket.sendto(finPackage, addr)
                if(client_socket.recv(buffer1)):
                    print("Ending connection...")
                    f.close()
                    client_socket.close()
            


if args.server and args.client:
    print("Can't run server and client at the same time")
    sys.exit()

if not args.server and not args.client:
    print("You have to start in either client or server mode")
    sys.exit()


if args.reliable_method == 'stop_and_wait':
    stop_and_wait()
elif args.reliable_method == 'GBN':
    GBN()
elif args.reliable_method == 'SR':
    SR()




'''

if args.server:
    acknum = 1
    addr = (args.bind, args.port)
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((args.bind, args.port))
    f = open("test2.png", "wb")
    data, addr = serverSocket.recvfrom(buffer1)
    header_msg = data[:12]
    seq, ack, flags, win  = headers.parse_header(header_msg)
    syn, ack, fin = headers.parse_flags(flags)
    i = 0
    if(syn > 0):
        seq = 1
        flags = 12
        SynAckPackage = headers.create_packet(seq, ack, flags, 0, b'')
        serverSocket.sendto(SynAckPackage, addr)
        if(serverSocket.recvfrom(buffer1)):
            print("successfully established connection")
            while True:
                data, addr = serverSocket.recvfrom(buffer1)
                print("Receiving data...")
                message_body = data[12:]
                seq, ack, flags, win = headers.parse_header(data[:12])
                syn, ack , fin = headers.parse_flags(flags)
                if(fin > 0):
                    flags = 4
                    data = headers.create_packet(seq, ack, flags, 0, b'')
                    f.close()
                    serverSocket.sendto(data, addr)
                    serverSocket.close()
                    print("Shutting down server...")
                    sys.exit()
                else:
                    if args.test_case == "skip_ack":
                        i+=1
                        if i == 3:
                            continue
                        f.write(message_body)
                        flags=4
                        AckMessage = headers.create_packet(seq, ack, flags, 0, b'')
                        serverSocket.sendto(AckMessage, addr)
                    else:
                        f.write(message_body)
                        flags=4
                        AckMessage = headers.create_packet(seq, ack, flags, 0, b'')
                        serverSocket.sendto(AckMessage, addr)

   '''         
    

    
'''        
    print(f'seq={seq}, ack={ack}, flags={flags}')
    header = headers.create_packet(0,1,0,0, b'')
    serverSocket.sendto(header, addr)
    #print("Received file: ", data.strip())
    f = open(args.file, "wb")
    data, addr = serverSocket.recvfrom(buffer1)
    while data:
        acknum += 1
        print(len(data),"Total size of data")
        header_from_msg = data[:12]
        seq, ack, flags, win = headers.parse_header(header_from_msg)
        print("Header from sender: ", header_from_msg)
        message_Body = data[12:]
        decodemessage = message_Body.strip()
        print(decodemessage)
        if acknum == 6:
            data, addr = serverSocket.recvfrom(buffer1)
            body = data[12:]
            ackMsg = headers.create_packet(0,acknum, 0 ,0 , b'')
            serverSocket.sendto(ackMsg,addr)
        else:
            f.write(message_Body)
            ackMsg = headers.create_packet(0,acknum, 0 ,0 , b'')
            serverSocket.sendto(ackMsg,addr)
            print("message body", message_Body)
            print("message body size: ", len(message_Body))
            print(f'seq={seq}, ack={ack}, flags={flags}')
            data, addr = serverSocket.recvfrom(buffer1)
    print("closing server")
    serverSocket.close()
'''



'''
if args.client:
    addr = (args.bind, args.port)
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.connect((args.bind, args.port))
    client_socket.settimeout(2)
    f = open(args.file, "rb")
    filedata = f.read(buffer)
    #print(filedata)
    seq = 1
    acknum = 0
    flags = 8
    synpack = headers.create_packet(0,acknum,flags,0, b'')
    receiveSynAck= ""
    while True:
        client_socket.sendto(synpack, addr)
        try:
            receiveSynAck = client_socket.recv(1472)
            break
        except Timeout:
            continue
    headersAck = receiveSynAck[:12]
    seq, ack, flags, win = headers.parse_header(headersAck)
    syn, ack, fin = headers.parse_flags(flags)
    if(syn>0 and ack> 0):
        seq = 0
        ack = 1
        flags = 4
        sendAck = headers.create_packet(seq,ack, flags,0,b'') 
        if(client_socket.sendto(sendAck, addr)):
            print("connection successfully established")
            while filedata:
                message = headers.create_packet(seq,ack,flags,0,filedata)
                while True:
                    try:
                        client_socket.sendto(message, addr)
                        serverAck = client_socket.recv(buffer1)
                        sSeq, sAck, sFlags, sWin  = headers.parse_header(serverAck[:12])
                        print(f"seq={sSeq}, sAck={sAck}, sFlags={sFlags}")
                        break
                    except timeout:
                        continue
                filedata = f.read(buffer)
            flags = 2 
            finMsg = headers.create_packet(seq, ack,flags,0, b'')
            while True:
                try:
                    client_socket.sendto(finMsg, addr)
                    if(client_socket.recv(buffer)):
                        print("closing connection...")
                        client_socket.close()
                        f.close()
                    break
                except timeout:
                    continue
'''



"""
    print(f)
    print("connected to host")
    #first_pack = headers.create_packet(acknum,0,0,0,filedata)
    #client_socket.sendto(first_pack, addr)
    while filedata:
        #print("in loop")
        print(filedata)
        client_socket.settimeout(2)
        data = headers.create_packet(0, acknum, 0, 0, filedata)
        #print(len(data))
        client_socket.sendto(data, addr)
        try:
            server_message= client_socket.recv(1024)
            recvdata = server_message[:12]
            seq, ack, flags, win = headers.parse_header(recvdata)
            print(f'seq={seq}, ack={ack}, flags={flags}')
            print(server_message)
            filedata = f.read(buffer)
        except timeout:
            repeatSend(client_socket, addr, data)
        acknum+=1
        # recvMsg = client_socket.recv(buffer)
        #print(recvMsg)
    byeData = headers.create_packet(acknum, 0,0,0, "BYE".encode())
    client_socket.sendto(byeData, addr)
    recieve_bye = client_socket.recv(1024)
    if(recieve_bye.split() == "BYE"):
        f.close()
        client_socket.close()
"""
