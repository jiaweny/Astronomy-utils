import json,time,sys,os,requests
from collections import OrderedDict

# how many second to sleep
SLEEP_SEC=1
# max number of time to check response
LOOP_COUNTER=60
# keeping sys.stdout
old_stdout=sys.stdout


def tns_search(ra,dec,radius=3, api_key='', url="https://www.wis-tns.org/api/get/search"):
    json_list=[("ra","%s"%ra), ("dec","%s"%dec), ("radius","%s"%radius), ("units","arcsec"), 
            ("objname",""), ("objname_exact_match",0), ("internal_name",""), 
            ("internal_name_exact_match",0), ("objid",""), ("public_timestamp","")]   
    try:
        # url for search obj
        search_url=url+'/search'
        # change json_list to json format
        json_file=OrderedDict(json_list)
        # construct a dictionary of api key data and search obj data
        search_data={'api_key':api_key, 'data':json.dumps(json_file)}
        # search obj using request module
        response=requests.post(search_url, data=search_data)
        # return response
        return response
    except Exception as e:
        return [None,'Error message : \n'+str(e)]
    
    
def tns_exist(ra,dec, radius=3,url="https://www.wis-tns.org/api/get/search",api_key=''): #"https://sandbox.wis-tns.org/api/get"
    '''
    Given ra and dec, and radius in arcsec, return True if already exists on TNS, otherwise return false
    '''
    response = tns_search(ra, dec, radius=radius, url=url, api_key=api_key)

    if len(json.loads(response.content)['data']['reply'])>0: return True
    return False

def tns_snname(ra,dec, radius=3,url="https://www.wis-tns.org/api/get/search",api_key=''): #"https://sandbox.wis-tns.org/api/get"
    '''
    Given ra and dec, and radius in arcsec, return snname at given position if any
    '''
    response = tns_search(ra, dec, radius=radius, url=url, api_key=api_key)
    names = [ii['objname'] for ii in json.loads(response.content)['data']['reply']]
    if len(names)==1:
        names = names[0]
    return names


def non_detection(nodet_jd, nodet_f, nodet_lm):
    '''
    Create non-detection for json report
    '''
    if nodet_f == 0: return ""
    filt_code = {'g':"21", 'r': "22", 'i':"23", 'z':"24"}
    non_detection= {"non_detection": {
        "obsdate": "%s"%nodet_jd,
        "limiting_flux": "%s"%nodet_lm,
        "flux_units": "1", #AB mag
        "filter_value": "%s"%filt_code[nodet_f],
        "instrument_value": "172", # ctio 4m decam
        "exptime": "",
        "observer": "",
        "comments": "",
        "archiveid": "",
        "archival_remarks": ""
      }}
    return non_detection['non_detection']

def create_photometry_group(mjd, mag, magerr, filt):
    '''
    Create photometry group for json report
    '''
    photometry_group = {}
    ii = 0

    filt_code = {'g':"21", 'r': "22", 'i':"23", 'z':"24"}
    for dd, mm, merr, ff in zip(mjd, mag, magerr, filt):
        photometry_group["%s"%ii] = {
            "obsdate": "%s"%dd,
            "flux": "%s"%mm,
            "flux_error": "%s"%merr,
            "flux_units": "1", # ABMag
            "filter_value": filt_code[ff],
            "instrument_value": "172", # ctio 4m decam
#             "limiting_flux": "",
#             "exptime": "",
#             "observer": "",
#             "comments": ""
          }
        ii += 1
    return {"photometry_group": photometry_group}

def create_at_entry(ra, dec, JD, photometry_group, non_detection="", related_files=""):
    '''
    ra, dec needs to be in degrees.
    JD: discovery JD YYYY-MM-DD.float or  float JD
    photometry_group: "photometry_group": {
          "0": {
            "obsdate": "2020-03-01.234",
            "flux": "19.5",
            "flux_error": "0.2",
            "limiting_flux": "",
            "flux_units": "1",
            "filter_value": "50",
            "instrument_value": "103",
            "exptime": "60",
            "observer": "Robot",
            "comments": ""
          },
          "1": {
            " obsdate ": "",
            " flux ": "",
            "flux_error": "",
            "limiting_flux": "",
            " flux_units ": "",
            " filter_value ": "",
            " instrument_value ": "",
            "exptime": "",
            "observer": "",
            "comments": ""
          }
    non_detection:"non_detection": {
        "obsdate": "2020-02-28.123",
        "limiting_flux": "21.5",
        "flux_units": "1",
        "filter_value": "50",
        "instrument_value": "103",
        "exptime": "60",
        "observer": "Robot",
        "comments": "",
        "archiveid": "",
        "archival_remarks": ""
      },
    related_files: "related_files": {
        "0": {
          "related_file_name": "rel_file_1.png",
          "related_file_comments": "Finding Chart..."
        },
        "1": {
          "related_file_name": "rel_file_2.jpg",
          "related_file_comments": "Discovery image..."

    '''
    entry = {}
    entry["ra"] = {
        "value": str(ra),
        "error": "",
        "units": "deg"
    }

    entry["dec"] = {
        "value": str(dec),
        "error": "",
        "units": "deg"
    }

    entry["reporting_group_id"]= "114"  # our DESIRT group id.
    entry["discovery_data_source_id"]="114"  # DESIRT
    entry["reporter"]= "Xingzhuo Chen (Texas A&M U.), Lei Hu (Purple Mountain Observatory),\
        Jiawen Yang (Texas A&M U.), Jian Tao (Texas A&M U.), Lifan Wang (Texas A&M U.),\
        Xiaofeng Wang (Tsinghua University), Antonella Palmese (KICP), Dietrich Baade (ESO),\
        Segev BenZvi (U. of Rochester), Peter Brown (Texas A&M U.), Jeffery Cooke (Swinburne U.), Kyle Dawson (The University of Utah), \
        Melissa Graham (University of Washington), Ji-an Jiang (The University of Tokyo), Alex Kim (LBNL), \
        Anton Koekemoer (STSci), Wenxiong Li (Tel Aviv U.), Jeremy Mould (Swinburne U.), Peter Nugent (LBNL), \
        Ferdinando Patat (ESO), Syed A. Uddin (Carnegie Observatories), Jujia Zhang (Yunnan Astronomical Observatory)"

    entry["discovery_datetime"]= "%s" % JD
    entry["at_type"] = "1" #PSN
    entry["host_name"] = ""
    entry["host_redshift"] = ""
    entry["transient_redshift"] = ""
    entry["internal_name"] = ""
   # entry["internal_name_format"] = {
   #     "prefix": "prefixStr",
   #     "year_format": "YY",
   #     "postfix": "postfixStr"
   # }
    entry["remarks"] = ""
    entry["photometry"] = photometry_group
    entry["related_files"] = related_files

    if non_detection == "":
        non_detection = {
            #"obsdate": "",
            #"limiting_flux": "",
            #"flux_units": "",
            #"filter_value": "",
            #"instrument_value": "",
            #"exptime": "",
            #"observer": "",
            #"comments": "",
            "archiveid": "0",  # other
            "archival_remarks": "DECam Legacy Survey"
        }
    entry["non_detection"] = non_detection

    #entry = json.dumps(entry, indent = 4)
    return entry

def create_at_json(entries):
    '''
    given at entry defined in create_at_entry, create at json report
    '''
    ii = 0
    json_at = {"at_report":{}}
    for entry in entries:
        json_at["at_report"]["%s"%ii] = entry
        ii+=1
    return json_at

# function for changing data to json format
def format_to_json(source):
    # change data to json format and return
    parsed=json.loads(source,object_pairs_hook=OrderedDict)
    result=json.dumps(parsed,indent=4)
    return result


## ==============Below are functions taken from examples given on tns website============
# Disable print
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# function for sending json reports (AT or Classification)
def send_json_report(url,json_file_path,api_key):
    try:
        json_url=url+'/bulk-report'
        # read json data from file
        json_read=format_to_json(open(json_file_path).read())
        # construct a dictionary of api key data and json data
        json_data={'api_key':api_key, 'data':json_read}
        # send json report using request module
        response=requests.post(json_url, data=json_data)
        # return response
        return response
    except Exception as e:
        return [None,'Error message : \n'+str(e)]

# sending tsv or json report (at or class) and printing reply
def send_report(url, report, type_of_report,api_key):
    # sending report and checking response
    print ("Sending "+report+" to the TNS...")
    # choose which function to call
    if type_of_report=="tsv":
        response=send_tsv_report(url,report)
    else:
        response=send_json_report(url,report,api_key)
    response_check=check_response(response)
    # if report is sent
    if response_check==True:
        print ("The report was sent to the TNS.")
        # report response as json data
        json_data=response.json()
        # taking report id
        report_id=str(json_data['data']['report_id'])
        print ("Report ID = "+report_id)
        # sending report id to get reply of the report
        # and printing that reply
        # waiting for report to arrive before sending reply
        # for report id
        blockPrint()
        counter = 0
        while True:
            time.sleep(SLEEP_SEC)
            reply_response=reply(url,report_id,api_key)
            print(reply_response)
            reply_res_check=check_response(reply_response)
            if reply_res_check!=False or counter >= LOOP_COUNTER:
                break
            counter += 1
        enablePrint()
        print_reply(url,report_id, api_key)
    else:
        print ("The report was not sent to the TNS.")


# function that checks response and
# returns True if everything went OK
# or returns False if something went wrong
def check_response(response):
    # if response exists
    if None not in response:
        # take status code of that response
        status_code=int(response.status_code)
        if status_code==200:
            # response as json data
            json_data=response.json()
            # id code
            id_code=str(json_data['id_code'])
            # id message
            id_message=str(json_data['id_message'])
            # print id code and id message
            print ("ID code = "+id_code)
            print ("ID message = "+id_message)
            # check if id code is 200 and id message OK
            if (id_code=="200" and id_message=="OK"):
                return True
            #special case
            elif (id_code=="400" and id_message=="Bad request"):
                return None
            else:
                return False
        else:
            # if status code is not 200, check if it exists in
            # http errors
            if status_code in list(http_errors.keys()):
                print (list(http_errors.values())
                       [list(http_errors.keys()).index(status_code)])
            else:
                print ("Undocumented error.")
            return False
    else:
        # response doesn't exists, print error
        print (response[1])
        return False

# function for getting reply from report
def reply(url, report_id,api_key):
    try:
        # url for getting report reply
        reply_url=url+'/bulk-report-reply'
        # construct a dictionary of api key data and report id
        reply_data={'api_key':api_key, 'report_id':report_id}
        # send report ID using request module
        response=requests.post(reply_url, data=reply_data)
        # return response
        return response
    except Exception as e:
        return [None,'Error message : \n'+str(e)]

def enablePrint():
    sys.stdout.close()
    sys.stdout = old_stdout

# sending report id to get reply of the report
# and printing that reply
def print_reply(url,report_id, api_key):
    # sending reply using report id and checking response
    print ("Sending reply for the report id "+report_id+" ...")
    reply_res=reply(url, report_id, api_key)
    reply_res_check=check_response(reply_res)
    # if reply is sent
    if reply_res_check==True:
        print ("The report was successfully processed on the TNS.\n")
        # reply response as json data
        json_data=reply_res.json()
        # feedback of the response
        print(111)
        print('json_data',json_data)
        feedback=list(find_keys('feedback',json_data))
        print(feedback,'feedback')
        # check if feedback is dict or list
        if type(feedback[0])==type([]):
            feedback=feedback[0]
        # go trough feedback
        for i in range(len(feedback)):
            # feedback as json data
            json_f=feedback[i]
            # feedback keys
            feedback_keys=list(json_f.keys())
            # messages for printing
            msg=[]
            # go trough feedback keys
            for j in range(len(feedback_keys)):
                key=feedback_keys[j]
                json_feed=json_f[key]
                msg=msg+print_feedback(json_feed)
            if msg!=[]:
                print ("-----------------------------------"\
                       "-----------------------------------" )
                for k in range(len(msg)):
                    print (msg[k][0])
                    print (msg[k][1])
                print ("-----------------------------------"\
                       "-----------------------------------\n")
    else:
        if (reply_res_check!=None):
            print ("The report doesn't exist on the TNS.")
        else:
            print ("The report was not processed on the TNS "\
                   "because of the bad request(s).")

# find all occurrences of a specified key in json data
# and return all values for that key
def find_keys(key, json_data):
    if isinstance(json_data, list):
        for i in json_data:
            for x in find_keys(key, i):
               yield x
    elif isinstance(json_data, dict):
        if key in json_data:
            yield json_data[key]
        for j in list(json_data.values()):
            for x in find_keys(key, j):
                yield x

def print_feedback(json_feedback):
    # find all message id-s in feedback
    message_id=list(find_keys('message_id',json_feedback))
    # find all messages in feedback
    message=list(find_keys('message',json_feedback))
    # find all obj names in feedback
    objname=list(find_keys('objname',json_feedback))
    # find all new obj types in feedback
    new_object_type=list(find_keys('new_object_type',json_feedback))
    # find all new obj names in feedback
    new_object_name=list(find_keys('new_object_name',json_feedback))
    # find all new redshifts in feedback
    new_redshift=list(find_keys('new_redshift',json_feedback))
    # index counters for objname, new_object_type, new_object_name
    # and new_redshift lists
    n_o=0
    n_not=0
    n_non=0
    n_nr=0
    # messages to print
    msg=[]
    # go trough every message and print
    for j in range(len(message)):
        m=str(message[j])
        m_id=str(message_id[j])
        if m_id not in ['102','103','110']:
            if m.endswith('.')==False:
                m=m+'.'
            if m_id=='100' or  m_id=='101':
                m="Message = "+m+" Object name = "+str(objname[n_o])
                n_o=n_o+1
            elif m_id=='120':
                m="Message = "+m+" New object type = "+str(new_object_type[n_not])
                n_not=n_not+1
            elif m_id=='121':
                m="Message = "+m+" New object name = "+str(new_object_name[n_non])
                n_non=n_non+1
            elif m_id=='122' or  m_id=='123':
                m="Message = "+m+" New redshift = "+str(new_redshift[n_nr])
                n_nr=n_nr+1
            else:
                m="Message = "+m
            msg.append(["Message ID = "+m_id,m])
    # return messages
    return msg
