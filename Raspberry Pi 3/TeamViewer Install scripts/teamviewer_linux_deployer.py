# ============================
# TeamViewer Deployment Script
# ============================
# platform: Ubuntu 16.04
# synopsis: Automate download, install, accept EULA, setup password, add to computers and contacts, account assignment and enables easy acces. Additionaly, installs pip and requests.
# requires: python-pip, wget, requests
"""
Authors
Christian Cay
Guillermo Illana
Willian de Fazio
"""

import subprocess, re, sys, os, socket, time, smtplib, urllib2, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

class errorFunctions():
    @staticmethod
    def parse_exception(action_description=None,exception_object=None,variables=None):    
        variables_string = ''
        e_str = ''
        
        if type(action_description) != str:
            action_description = "Not Specified"
        
        
        if variables != None:
            try:
                variables_string = ' . variables:' +  str(variables) + '.'
            except:
                variables_string = ' . Could not convert variables to strings.'
                
        try:
            e_str = str(exception_object)
        except:
            e_str = "could not convert exception to string"
        
        output_string = 'expection occured while trying to: ' + action_description + ' .exception:' + e_str + variables_string
        return output_string

    @staticmethod    
    def log_exception(function_name=None,action_description=None,exception_object=None,variables=None):
        variables_string = ''
        if type(function_name) != str:
            function_name = "Not Specified"
        if type(action_description) != str:
            action_description = "Not Specified"
        
        if variables != None:
            try:
                variables_string = ' . variables:' +  str(variables) + '.'
            except:
                variables_string = ' . Could not convert variables to strings.'
                
        try:
            e_str = str(exception_object)
        except:
            e_str = "could not convert exception to string"    
        
        output_string = 'expection occured in function: ' + function_name + '. while trying to: ' + action_description + ' .exception: ' + e_str + ' variables: ' + variables_string
        print (output_string)
        return output_string
        



def get_serial():
    # Extract serial from cpuinfo file
    cpuserial = None
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        
        f.close()
    except Exception as e:
        errorFunctions.log_exception('get_serial', 'get_serial', e, f)
        cpuserial = None

    return cpuserial

def get_mac_address(interface=None):    
    
    try:
        mac = open('/sys/class/net/'+interface+'/address').readline()
    except Exception as e:
        errorFunctions.log_exception('get_mac_address','read location',e, interface)
        mac = None
    
    return mac[0:17]


def run():
    call_result = {}
    debug_data = []
    return_msg = 'run '


    # check connection
    connected = False
    while not connected:
        try:
            urllib2.urlopen('http://www.google.com', timeout=1)
            connected = True
        except urllib2.URLError as err:
            connected = False
            time.sleep(5)
    # </end> check connection

    # install pip if it is not installed and then install requests library.
    print subprocess.check_output(["apt-get", "install", "python-pip", "-y"])
    print subprocess.check_output(["pip", "install", "requests"])

    import requests  # only import this library if we actually need to send something, most times we won't

    # ======================
    # Configuration settings
    # ======================
    serial = None
    serial = "asdfasf235"
    mac_address = None
    mac_address = "2523524123"
    password = "cheddar1"
    # password should be at least 6 characters
    #testing API token
    #token = "4704408-hs48ywasIbkN0VUjWvQ8"
    #actual API token
    token = "7663587-WDkwhzEb40mLySa5Nipx"
    # script token, generated from the management console.
    groupid = "g158983244"
    # please include the g. Example: g123456
    
    # alias hostname is the default value    
    if serial != None and mac_address != None:
        alias = serial + '~' + mac_address
        print 'mac address:' + mac_address + ' serial:' + serial
    else:
        alias = socket.gethostname()
    
    description = alias

    if not os.geteuid() == 0:
        print 'TeamViewer installation script must be run as root.'
        return {"success": False, "return_msg": return_msg, "debug_data": debug_data}

    # install pip if it is not installed and then install requests library.
    # print subprocess.check_output(["apt-get","install","python-pip","-y"])
    # print subprocess.check_output(["pip","install","requests"])

    downloadurl = "https://download.teamviewer.com/download/linux/teamviewer-host_armhf.deb"
    downloadurl = "https://download.teamviewer.com/download/linux/teamviewer_i386.deb"
    apiurl = "https://webapi.teamviewer.com/api/v1/devices"

    print "TeamViewer installation script"
    print "This process might take a while, please wait..."

    print "1. Downloading TeamViewer"
    os.chdir("/tmp")
    print subprocess.check_output(["wget", downloadurl])

    print
    print "2. Installing"
    print subprocess.check_output(["apt-get", "update"])
    print subprocess.check_output(["dpkg", "-i", "teamviewer_i386.deb"])
    print subprocess.check_output(["apt-get", "install", "-fy"])

    print
    print "3. Accepting license agreement"
    print subprocess.check_output(["teamviewer", "daemon", "stop"])
    f = open("/opt/teamviewer/config/global.conf", "a")
    f.write("[int32] EulaAccepted = 1\n")
    f.close()
    print subprocess.check_output(["teamviewer", "daemon", "start"])

    print
    print "4. Setting unattended access password"
    print subprocess.check_output(["teamviewer", "passwd", password])

    # getting Teamviewer ID
    teamviewerinfo = subprocess.check_output(["teamviewer", "info"])
    print teamviewerinfo
    # mremoteid = re.search(r"TeamViewer ID:.*(\d{9})", teamviewerinfo, re.MULTILINE)
    # remoteid = mremoteid.group(1)

    mremoteid = re.search(r"TeamViewer ID.*(\d+)", teamviewerinfo, re.MULTILINE)
    getTeamViewerID = re.search(r"\d+$", mremoteid.group(0))
    remoteid = getTeamViewerID.group(0)

    c = 1
    while (remoteid == "0") & (c < 6):
        time.sleep(5)
        # getting Teamviewer ID
        teamviewerinfo = subprocess.check_output(["teamviewer", "info"])
        print teamviewerinfo
        mremoteid = re.search(r"TeamViewer ID.*(\d+)", teamviewerinfo, re.MULTILINE)
        getTeamViewerID = re.search(r"\d+$", mremoteid.group(0))
        remoteid = getTeamViewerID.group(0)
        if c == 5:
            print "Timeout while getting the TeamViewer ID. Exit application..."
            return {"success": False, "return_msg": return_msg, "debug_data": debug_data}
    c += 1

    print
    print "5. Adding {0} to your computers and contacts".format(remoteid)
    payload = "{{ \"remotecontrol_id\" : \"r{0}\", \"groupid\" : \"{1}\", \"password\" : \"{2}\", \"alias\" : \"{3}\", \"description\" : \"{4}\" }}".format(
        remoteid, groupid, password, alias, description)
    headers = {
        'authorization': "Bearer " + token,
        'content-type': "application/json",
        'cache-control': "no-cache"
    }
    response = requests.request("POST", apiurl, data=payload, headers=headers)

    if response.status_code == 200:
        print "Device with name {0} added to computers and contacts to group ID {1}".format(alias, groupid)
    else:
        print "Something went wrong when adding device. Status code {0}".format(response.status_code)
        print "Error details: {0}".format(response.text)
        return {"success": False, "return_msg": return_msg, "debug_data": debug_data}

    print
    print "6. Enabling easy access in {0}".format(remoteid)

    url = "https://webapi.teamviewer.com/api/v1/devices"
    querystring = {"remotecontrol_id": "r{0}".format(remoteid)}
    response = requests.request("GET", url, headers=headers, params=querystring)
    remoteid = re.search(r"d\d+", response.text, re.MULTILINE)

    payload = "{{ \"device_id\" : \"{0}\", \"current_device_password\" : \"{1}\", \"enable_easy_access\" : \"{2}\"}}".format(
        remoteid.group(), password, True)

    apiurl = "https://webapi.teamviewer.com/api/v1/devices/assign/"
    response = requests.request("POST", apiurl, data=payload, headers=headers)

    if response.status_code == 200 or response.status_code == 204:
        print "Device with name {0} has Easy Access enable".format(alias)

    else:
        print "Something went wrong when adding device. Status code {0}".format(response.status_code)
        print "Error details: {0}".format(response.text)
        return {"success": False, "return_msg": return_msg, "debug_data": debug_data}

    print
    print "7. Process completed..."

    return {"success": True, "return_msg": return_msg, "debug_data": debug_data}



def log_exception(function_name=None, action_description=None, exception_object=None):
    if type(function_name) != str:
        function_name = "Not Specified"
    if type(action_description) != str:
        action_description = "Not Specified"

    try:
        e_str = str(exception_object)
    except:
        e_str = "could not convert exception to string"

    output_string = 'expection occured in function: ' + function_name + '. while trying to: ' + action_description + ' .exception:' + e_str
    return output_string


def sendEmail(email_body, to_mail=None):

    call_result = {}
    debug_data = []
    return_msg = 'sendEmail '

    serverSmtp = "smtp.gmail.com"
    emailID = 'dgnet_deployer@dgnet.cloud'
    emailPass = 'SeDF(*WE$J#To1zaFU@'

    if to_mail is None: to_mail = emailID

    subject = 'send email test subject'
    msg = MIMEMultipart()
    msg.attach(MIMEText(email_body, 'plain'))
    msg["From"] = emailID
    msg["To"] = "Dchevalier@red-threadcom"
    msg["Subject"] = subject
    try:
        server = smtplib.SMTP_SSL(serverSmtp, 465)
        server.ehlo()
        server.login(emailID, emailPass)
        server.sendmail(from_addr=emailID, to_addrs=to_mail, msg=msg.as_string())
        server.close()

        print('Email sent!')
    except Exception as e:
        e_str = log_exception("sendEmail", "sending logs email", e)
        debug_data.append(e_str)
        return_msg += "sending email failed while connecting to server and actually sending mail"
        return {"success": False, "return_msg": return_msg, "debug_data": debug_data}

G_runned_flag_dir = "/opt/teamviewer/config/"

if __name__ == "__main__":
    call_result = {}
    debug_data = []
    return_msg = '__main__ '

    if os.path.isfile(G_runned_flag_dir + ".runned"):
        sys.exit("already runned")
    else:
        orig_stdout = sys.stdout
        log_file_path = '/tmp/teamviewer_installation_logs.txt'
        f = open(log_file_path, 'w')
        sys.stdout = f

        try:
            call_result = run()
            if call_result.get("success") == True:
                # setting runned flag which is checked above
                with open(G_runned_flag_dir + ".runned", 'w') as f:
                    f.write("")
        except Exception as e:
            err_str = log_exception("__main__", "run on top level", e)
            print(err_str)

        sys.stdout = orig_stdout
        f.close()

        # sending mail with gathered logs
        log_file = open(log_file_path, 'r')
        sendEmail("".join(log_file.readlines()))
        log_file.close()
        while True:
            try:
                subprocess.check_output(["killall", "TeamViewer"])
            except:
                pass
            time.sleep(30)
        




