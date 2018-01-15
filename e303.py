# SMS send and receive module using HTTP post method over Huawei H303 3G module
# H303 module must be Ethernet mode (Device ID 12d1:14db)

# Following are the address for HTTP post & request method
#3G
# Get 3G signal strength
# api/monitoring/status
# Connection statics
# api/monitoring/traffic-statistics
# dial up connection
# api/dialup/connection
# Hand over setting

#SMS
# Check notification (see unread message etc)
# api/monitoring/check-notifications

# SMS Methods
# api/sms/sms-count
# api/sms/sms-list
# api/pb/pb-match
# api/sms/delete-sms
# api/sms/backup-sim
# api/sms/set-read
# config/sms/config.xml
# api/sms/save-sms
# api/sms/send-status
# api/sms/cancel-send

# Wifi stuff
# Wifi station config, just get error
# api/wlan/station-information
# Get wifi signal strength etc.
# api/wlan/station-information
# wlan setting
# api/wlan/multi-basic-settings
# api/wlan/multi-security-settings
# api/wlan/handover-setting
# config/wifistation/config.xml

# Device
# Get Plum name
# api/net/current-plmn
# Get sim infos
# api/monitoring/converged-status
# api/pin/status
# Get device info
# api/device/information
# Get basic settings
# api/wlan/basic-settings
# Get device's autorun Version
# api/device/autorun-version

# Something else
# api/host/info
# config/pcassistant/config.xml
# Global config
# config/global/config.xml
# Module switch
# api/global/module-switch
# config/ota/config.xml
# OTA
# config/ota/config.xml

# Log in management
# user state login
# api/user/state-login

import time, requests, sys
from bs4 import BeautifulSoup
# Using Lxml to speed up faster parsing, Lxml is used also for writing xml
from lxml import etree, objectify

E303_ip = 'http://192.168.1.1/'
HTTPPOST_SEND = 'api/sms/send-sms'
HTTPPOST_RECEIVE = 'api/sms/sms-list'
HTTPPOST_SET_READ = 'api/sms/set-read'
HTTPPOST_CHECK_NOTIFICATION = 'api/monitoring/check-notifications'
HTTPPOST_DELETE = 'api/sms/delete-sms'
HTTPPOST_COUNT = 'api/sms/sms-count'
HTTPPOST_STATUS = "api/monitoring/status"

# //Connection status
CONNECTION_CONNECTING = '900'
CONNECTION_CONNECTED = '901'
CONNECTION_DISCONNECTED = '902'
CONNECTION_DISCONNECTING = '903'
NET_WORK_TYPE_NOSERVICE = '0'

CONNECTION_STATUS = {NET_WORK_TYPE_NOSERVICE: 'NOSERVICE',
CONNECTION_CONNECTING : 'CONNECTING',
CONNECTION_CONNECTED : 'CONNECTED',
CONNECTION_DISCONNECTED : 'DISCONNECTED',
CONNECTION_DISCONNECTING : 'DISCONNECTING'}

NETWORK_TYPE = {'1': 'GSM',
                '2': 'GPRS',
                '3': 'EDGE',
                '4': 'WCDMA',
                '5': 'HSDPA',
                '6': 'HSUPA',
                '7': 'HSPA',
                '8': 'TDSCDMA',
                '9': 'HSPA_PLUS',
                '10': 'EVDO_REV_0',
                '11': 'EVDO_REV_A',
                '12': 'EVDO_REV_A',
                '13': '1xRTT',
                '14': 'UMB',
                '15': '1xEVDV',
                '16': '3xRTT',
                '17': 'HSPA+64QAM',
                '18': 'HSPA+MIMO',
                '19': 'LTE'}

# Logger
# import logging
# logging.basicConfig()
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

######## Trivial text checker for simple responces to httprequest #####
def get_word(text, word):
    word_length = len(word)
    for i in range(len(text)):
        k = i + word_length
        if text[-k : -i] == word:
            return True
    return False

def get_value(text, tag):
    tag = "<" + tag + ">"
    tag_length = len(tag)
    for i in range(len(text)):
        k = i + tag_length
        # print(text[i : k])
        # Scan texts from front until get tag
        if text[i] == "<":
            if text[i : k] == tag:
                for j in range(k, len(text) - tag_length):
                    if text[j] == "<":
                        # print('j: ', j)
                        # print('k: ',k)
                        if j == k + 1:
                            value = text[k]
                        else:
                            value = text[k: j]
                        # print ("got value:", value)
                        return value
    return False

def check_connection():
    a = requests.get(E303_ip + HTTPPOST_STATUS)
    if a.status_code == 200:
        status = get_value(a.text,'ConnectionStatus')
        if status == CONNECTION_CONNECTED:
            return True
    return False

def check_connection_detailed():
    a = requests.get(E303_ip + HTTPPOST_STATUS)
    # print(a.text)
    if a.status_code == 200:
        # a_parsed = BeautifulSoup(a.text, 'lxml')
        # print(a_parsed)
        status = get_value(a.text,'ConnectionStatus')
        # print (status)
        try:
            signal_status = CONNECTION_STATUS[status]
        except:
            signal_status = 'None'
        signal_strength = int(get_value(a.text, 'SignalStrength'))
        nt = get_value(a.text, 'CurrentNetworkType')
        try:
            network_type = NETWORK_TYPE[nt]
        except:
            network_type = 'None'

        return signal_status, signal_strength, network_type
    return False

def check_sent(sent_number, debug):
    a = requests.get(E303_ip + "api/sms/send-status")
    if debug: print(a.text)
    if a.status_code == 200:
        a_parsed = BeautifulSoup(a.text, 'lxml')
        phone = a_parsed.phone.string
        suc_phone = a_parsed.sucphone.string
        fail_phone = a_parsed.failphone.string
        if (phone is None and fail_phone is None) and suc_phone == sent_number:
            return True
    return False

def set_read_sms(msg_id):
    msg_index = []
    if isinstance(msg_id, int):
        msg_index.append(str(msg_id))
    elif isinstance(msg_id, str):
        msg_index.append(msg_id)
    else:
        msg_index = msg_id

    sent = 0
    if len(msg_index) > 0:
        for i in msg_index:
            # print("set read: ", i)
            request = objectify.Element("request")
            request.Index = i
            payload = etree.tostring(request)
            # print(payload)
            a = requests.post(E303_ip + HTTPPOST_SET_READ, data = payload)
            # print (a.text)
            # print (a.status_code)
            if a.status_code == 200:
                if get_word(a.text, "OK"):
                    sent += 1
        if sent == len(msg_index): return True
    return False

def extract_sms_content(msg):
    try:
        stat = msg.smstat.string
        # Move two siblings to get Index value, since .index is assigned differently
        index = msg.smstat.nextSibling
        index = index.nextSibling.string
        phone = msg.phone.string
        content = msg.content.string
        date = msg.date.string
        return stat, index, phone, date, content
    except:
        return ["","","","",""]

def sms_receive_request(page, counts, box, sorting):
    request = objectify.Element("request")
    request.PageIndex = page
    request.ReadCount = counts
    # Mailbox type 0: Draft? 1: Inbox, 2: outbox
    request.BoxType = box
    # Sort type 0: Date, 1: Message content? 2: Index
    request.SortType = 0
    # Ascending: 1
    request.Ascending = sorting
    #  Not really working this flag somehow messes up sorting
    request.UnreadPreferred = 0
    return etree.tostring(request)

def check_new_sms():
    a = requests.get(E303_ip + HTTPPOST_CHECK_NOTIFICATION)
    # a_parsed = BeautifulSoup(a.text, 'lxml')
    new_messages = get_value(a.text, "UnreadMessage")
    try:
        if int(new_messages) > 0:
            return True
    except:
        return False
    # print(a.text)
    # try:
    #     new_messages = int(a_parsed.unreadmessage.string)
    #     if new_messages > 0:
    #         return True
    # except TypeError:
    #     return False
    # return False

def count_new_sms():
    a = requests.get(E303_ip + HTTPPOST_CHECK_NOTIFICATION)
    new_messages = get_value(a.text, "UnreadMessage")
    try:
        new = int(new_messages)
        return new
    except:
        return 0

def get_new_sms(log):
    message_index = []
    content = []
    number = []
    # Check new sms in mail box
    if check_new_sms():
        new_messages = count_new_sms()

        fetch_all = False
        page = 1
        unreads = 0
        while not fetch_all:
            # Retrieve SMS from mail box
            counts = 5
            payload = sms_receive_request(page, counts, SMS_INBOX, SMS_DESCENDING)
            # Httprequest to http host 192.168.1.1
            sms_html = requests.post(E303_ip + HTTPPOST_RECEIVE, data = payload)
            if sms_html.status_code == 200:
                # print(sms_html.text)
                sms_parsed = BeautifulSoup(sms_html.text, 'lxml')
                # Put all messages in List
                messages = sms_parsed.find_all("message")
                # Exception handling in case all message was retrieved from inbox
                message_count = str(sms_parsed.count.string)
                if message_count == 0:
                    fetch_all = True
                # Count up all <message> tag
                # message_count = len(messages)

                # Search unread message from all messages
                for msg in messages:
                    read = msg.smstat.string
                    if read == '0':
                        msg_stat, msg_index, msg_phone, msg_date, msg_content = extract_sms_content(msg)
                        # Filter out if the number is from telephone company or junk / AD
                        if verify_number(msg_phone):
                            log.general_logging("New message: " + msg_index + " " + msg_phone + " " + msg_content)
                            number.append(msg_phone)
                            message_index.append(msg_index)
                            content.append(msg_content)
                        else:
                            # Set the message and ignore in case it is junk
                            if set_read_sms(msg_index):
                                log.general_logging("Set as junk: " + msg_index + " " + msg_phone + " " + msg_content)
                                # print ("set read: ", msg_index)
                        unreads += 1
                        if new_messages <= unreads:
                            fetch_all = True

                page += 1   # Inclement page
                # Exception handling, this should not be called.
                if page > SMS_MAX_CAPACITY / counts:
                    fetch_all = True
    return message_index, content, number

def verify_number(num):
    # If the number is shorter than 10, regard it as not from personal phone number
    if len(num) <= PHONE_MINIMUM_LENGTH:
        return False
        # If the number does not start from '+', regard it as not from personal phone
    elif num[0] != '+':
        return False
    else:
        return True



def list_sms(sms_counts, box, sorting, debug):
    # Maxmum sms listing is 50!
    counts = []
    if sms_counts > SMS_LIST_MAX:
        for cnt in range (sms_counts // SMS_LIST_MAX):
            counts.append(SMS_LIST_MAX)
            counts.append(sms_counts % SMS_LIST_MAX)
    else:
        counts.append(sms_counts)

    # print(sms_counts , SMS_LIST_MAX, sms_counts % SMS_LIST_MAX)
    # print(str(counts))
    page = 0
    all_message_indexes = []
    all_messages = []

    for count in counts:
        page += 1
        payload = sms_receive_request(page, count, box, sorting)
        sms_html = requests.post(E303_ip + HTTPPOST_RECEIVE, data = payload)

        # Display sms content
        if debug: print(sms_html.text)
        # Parsing html-tagged SMS contents with BeautifulSoup
    #     sms_parsed = BeautifulSoup(sms_html.text, 'html.parser')
        sms_parsed = BeautifulSoup(sms_html.text, 'lxml')

        # Find first message tag
        message = sms_parsed.message

        # Count up all <message> tag
        messages = sms_parsed.find_all("message")
        message_count = len(messages)

        if message_count > 0:
            # save all messages
            for msg in messages:
                msg_stat, msg_index, msg_phone, msg_date, msg_content = extract_sms_content(msg)
                all_message_indexes.append(msg_index)
                all_messages.append(msg_content)
    return all_message_indexes, all_messages

def timestamp():
    # Formatting time stamp
    time_stamp = time.strftime("%Y")
    time_stamp += '-'
    time_stamp += time.strftime("%m")
    time_stamp += '-'
    time_stamp += time.strftime("%d")
    time_stamp += ' '
    time_stamp += time.strftime("%H")
    time_stamp += ':'
    time_stamp += time.strftime("%M")
    time_stamp += ':'
    time_stamp += time.strftime("%S")
    return time_stamp

def send_sms(phone_no, sms_text):
    if isinstance(sms_text, str):
        # Formatting request
        request = objectify.Element("request")
        request.Index = -1
        request.Phones = ''
        request.Phones.Phone = phone_no
        request.Sca = ''
        request.Content = sms_text
        request.Length = str(len(sms_text))
        request.Reserved = 1
        request.Date = timestamp()
        payload = etree.tostring(request)
        a = requests.post(E303_ip + HTTPPOST_SEND, data = payload)
        # print(a)

def delete_sms(index_no):
    # Formatting request
    request = objectify.Element("request")
    request.Index = str(index_no)
    payload = etree.tostring(request)
    a = requests.post(E303_ip + HTTPPOST_DELETE, data = payload)

    if a.status_code == 200:
        if get_word(a.text, "OK"):
            # print("deleted %s" % index_no)
            return True
    return False

def count_sms():
    a = requests.get(E303_ip + HTTPPOST_COUNT)
    # print (a.text)
    if a.status_code == 200:
        a_parsed = BeautifulSoup(a.text, 'lxml')
        try:
            inbox = int(a_parsed.localinbox.string)
            outbox = int(a_parsed.localoutbox.string)
            return inbox, outbox
        except:
            return False
    return False

def clear_sms(box, counts):
    clear_enable = False
    # Check sms counts in mailbox so you won't delete more than you can
    inbox_now, outbox_now = count_sms()
    if box == SMS_INBOX:
        if counts < inbox_now:
            clear_enable = True
    elif box == SMS_OUTBOX:
        if counts < outbox_now:
            clear_enable = True
    # Cleaning sms
    if clear_enable:
        cleared = 0
        # Get sms list from younger ID
        indexes, messages = list_sms(counts, box, SMS_ASCENDING, SMS_LIST_DEBUG)
        # print ("Mail counts: ", indexes, messages)
        # Delete sms from younger index No.
        for sms_index in indexes:
            if delete_sms(sms_index):
                cleared += 1
                # print(sms_index)
        return cleared
    else:
        return 0

if __name__ == '__main__':
    import sys
    import getopt
    usage = 'Usage: python3 sms.py -p "123467890" -m "your message\n"'
    usage += '-b: Count sms in mailbox\n-c: Check connection status\n'
    usage += '-d "index_no": Delete a sms with index no\n-h: Showing help\n'
    usage += '-i [mail counts]: List inbox messages\n-o [mail counts]: List outbox messages\n'
    usage += '-n: Get new sms\n-r "Index No.": Set read sms with index no\n'
    usage += '-p "Phone number": Phone number\n-m "message": Message content\n'
    usage += '-s [mail counts]: Check sent status'

    message = 'Hi'  # Test Message
    test_phonenumber = '01234567890'

    if (len(sys.argv) > 1):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "bcd:hi:o:nr:p:m:s")
        except getopt.GetoptError:
            print(usage)
            sys.exit(2)

        for opt, arg in opts:
            if opt == '-b': #count sms in mailbox
                print(count_sms())
                sys.exit()
            elif opt == '-c': #check connection
                print(check_connection_detailed())
                if check_connection():
                    print("Connected")
                sys.exit()
            elif opt in ("-d"): #delete a sms with index no.
                index_no = arg
                delete_sms(index_no)
                sys.exit()
            elif opt == '-h': #showing help
                print (usage)
                sys.exit()
            elif opt == '-i': #list inbox sms
                counts = int(arg)
                print(list_sms(counts, SMS_INBOX, SMS_DESCENDING, True))
                sys.exit()
            elif opt == '-o': #list outbox sms
                counts = arg
                print(list_sms(counts, SMS_OUTBOX, SMS_DESCENDING, True))
                sys.exit()
            elif opt == '-n': #get new sms
                if(check_new_sms()):
                    import activity_logging
                    log = activity_logging.Logging()
                    print("got new sms!")
                    print(count_new_sms())
                    print(get_new_sms(log))
                else:
                    print("No new sms")
                sys.exit()
            elif opt in ("-r"): #set read sms with index no.
                index_no = []
                index_no.append(arg)
                if set_read_sms(index_no):
                    print("set read:", str(index_no))
                else:
                    print("Error:", str(index_no))
                sys.exit()
            elif opt in ("-p"): #phone number
                phonenumber = arg
            elif opt in ("-m"):
                message = arg
            elif opt == '-s': #check sent status
                check_sent(test_phonenumber, True)
                sys.exit()
        send_sms(test_phonenumber, message)
    else:
        get_new_sms()
