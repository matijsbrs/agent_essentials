# rename this file to: environment_defaults.py
# Be sure NOT to add it to your (public) git repository!

import os

os.environ.setdefault("APP_MAJOR_VERSION","0")
os.environ.setdefault("APP_MINOR_VERSION","3")
os.environ.setdefault("APP_BUILD","1")

# TTS (The Things Stack) v3 setup
os.environ.setdefault("TTN_HOST","eu1.cloud.thethings.network")
os.environ.setdefault("TTN_APPEUI",'Lighting' )
os.environ.setdefault("TTN_APPID",'tc3' )
os.environ.setdefault("TTN_TENANTID",'TenantID' )
os.environ.setdefault("TTN_CLIENT_ID","location.unibroker.ttn")
os.environ.setdefault("TTN_PASSWORD","MySecretKey")
