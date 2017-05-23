

get_dd_service_url=r'https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer/exts/CadastralSpecialServices/GetLatLon'

import requests
import csv
import os,sys
from datetime import datetime


csv_file=""
try:
    csv_file=sys.argv[1]
except:
    print """
This utility will return the centroid of the Cadastral Land Description and store the results in a .csv file.
The input data needs to be in the web-service format.  This data is derived from the BLM hosted web-service:
    %s

Required Input -
    CSV_FILE in the following format:
        <land_description_id,<land description>
    Example:
        record_1,NM230100N0050E0SN280
        record_2,NM230100N0050E0SN280
        record_3,NM230100N0050E0SN280


Usage:
        python.exe get_dd.py <PATH_TO_INPUT_CSV_FILE>
    """%get_dd_service_url
    sys.exit()

splt=os.path.splitext(csv_file)
output_csv_file=splt[0]+"-RESULTS_%s"%datetime.strftime(datetime.now(),"%Y%m%d_%H%M")+splt[1]
del splt

print "Writing Output to %s"%output_csv_file


csvw_file=open(output_csv_file,'wb')
csw=csv.writer(csvw_file)
s=requests.session()
with open(csv_file) as f:
    r = csv.reader(f)
    for row in r:
        if len(row)==1:
            csvw.writerow([row[0],"No Data Input"])
        if len(row)==0:
            continue

        # Get the DD
        xy=None
        resp=s.get(get_dd_service_url+"?f=json&trs=%s"%row[1])
        if resp.status_code == 200:

            if resp.json().has_key("status"):
                if resp.json().get("status") == "success":
                    if len(resp.json().get("coordinates"))>0:
                        xys=resp.json().get("coordinates")[0]
                        plssid=xys.get("plssid")
                        lat=xys.get("lat")
                        lon=xys.get("lon")
                        csw.writerow([row[0], plssid, lat, lon])
                    else:
                        csw.writerow([row[0],"no coordinates found"])
            elif resp.json().has_key("error"):
                error_data=resp.json().get("error")
                csvw.writerow([row[0],"ERROR {code} - {msg}".format(code=error_data.get("code"),msg=error_data.get("message"))])
        else:
            csw.writerow([row[0],"ERROR {sc} - {msg}".format(sc=str(resp.status_code),msg="HTTP Communication Error")])
            #except:
            #    csw.writerow(row[0],"FAILED TO PARSE %s"%resp.text)

del csw
del csvw_file


