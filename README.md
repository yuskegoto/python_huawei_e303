# A python script for Huawei E303 3G dongle
I wrote this python script for a project using Huawei E303. This script enables sending and receiving SMS, as well as retrieving basic network status. The module must be Ethernet mode, since the script uses HTTP post method. I have tested on Raspberry Pi, but theoretically it should work on any system. Please do research for hooking up E303.

## About Huawei E303
I heard there are various version of E303 out there. While early modules works as serial modem, later version installs a driver and let PC recognise as Ethernet module. In this mode you cannot use for example smsd. Writing AT command to the modem is also not possible. But you can still access SMS box with http post method as mentioned <a href="https://stackoverflow.com/questions/37833592/cant-read-or-count-messages-on-gsm-modem">here</a>. This script is a Python implementation of this method. I found all methods from JS files in config page of the modem. However I did not implement all methods since there are some methods obviously not used for E303.

## Requirement
This script is written for Python 3. But it won't be difficult to re-write it for Python 2.This script requires python <a href="http://docs.python-requests.org/en/master/">requests<a> <a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/">BeautifulSoup</a>, <a href="http://lxml.de/">lxml</a>.

## Hook up guide for Linux user
The modem changes it’s mode according to configuration. On the first plug in it shows up as a mass storage device, so windows users can install driver, which is however not necessary and obstruct using the modem for Linux user.
To force the modem to change mode, you have to istall <a href="http://www.draisberghof.de/usb_modeswitch/">usb-modemswitch</a>.

<i>sudo apt-get install usb-modeswitch</i>

Configure usb-modeswitch config file
<i>Preconfig /etc/usb_modeswitch.conf
#Huawei E303
DefaultVendor = 0x12d1
DefaultProduct = 0x1f01
</i>

Put config file on /etc/usb_modeswitch.d/12d1:1f01 :
<i>sudo nano  /etc/usb_modeswitch.d/12d1\:1f01</i>

<i>
#Huawei E303
DefaultVendor= 0x12d1
DefaultProduct= 0x1f01
TargetVendor= 0x12d1
TargetProduct= 0x1f01
MessageEndPoint = "0x01"
MessageContent="55534243000000000000000000000011060000000000000000000000000000"
NoDriverLoading=1
</i>

After configuring usb_modeswitch.conf, the 3G dongle will be recognized as LAN module and did not need further configuration
Check it by:
<i>Lsusb</i>
If everything went correct will show up as HSDPA modem.

## Further info
If you need to switch E303 to Serial Mode, check following thread
https://www.raspberrypi.org/forums/viewtopic.php?t=18996
