# DRTP---reliable-file-transfer-over-UDP
This is a project that implements three reliability protocols over UDP. The protocols include Stop and Wait, Go Back N and Selective Repeat. The main ability of 
this application is to transfer a file from client to server without having packets lost over transmission. 

The application uses argparser to input arguments. These arguments include:

* -c or --client is used to start the program in client mode
* -s or --server is used to start the program in server mode
* -i or --bind indicates which IP address the program will run on and has to be used when starting in both client and server mode
* -p or --port tells the program which port the program will run on
* -f or --file lets you choose which file you will transfer (Dont use same file for client and server. It might corrupt the file)
* -r or --reliable_method gives you a selection of protocols that the program will use to transfer a file. You can choose between: "Stop_a_Wait", "GBN" or "SR"
* -t or --test_case lets you choose which test you want to run in the program. E.g loss or skip_ack which will lead to either a loss in packet or not sending ack to client

Example of how to run the application:

Client:

`python3 application.py -c -i <-IP-Address> -p <"Port"> -f <Chosen-File> -r <Reliability-method> -t <Test-Case>`

Server:

 `python3 application.oy -s -i <-IP-Address> -p <-Port> -f <Chosen-File> -r <Reliablilty-method> -t <Test-Case>`


Keep in mind that you have to use the same reliablity method on server and client for the program to work as expected.


