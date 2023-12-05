"""
this script connects to the Spotify api and queries for the currently playing
song. It then queries for the Audio analysis of the song to find tatums,
which are the noticable beats and then sends a serial signal over COM8 where
an arduino board should be connected. These signals come at the same time as
the tatums in the song. This way the arduino board can flash lights with the
beat.
"""

import spotipy
import requests
import time
import serial
from spotipy.oauth2 import SpotifyOAuth
def findint(beats, prog):
    ite = 0
    while(ite < 10000):
        ite += 1
        if (ite + 2 > len(beats)):
            print("error")
            return -1
            break
        if(beats[ite]['start']<prog and beats[ite+1]['start']>prog):
            #print(beats[ite]['start'], "<", prog, "<", beats[ite+1]['start'])
            return ite
            break
    print("error")
    return -1
def getdata():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id=C_id, client_secret=C_sec, redirect_uri='http://localhost/', scope=scope,
                                  username='s6f2dioy7oy39ps3tfhxmclzg'))
    res = sp.current_user_playing_track()
    track_id = res['item']['id']
    prog = res['progress_ms'] / 1000
    r = requests.get(BASE_URL + 'audio-analysis/' + track_id, headers=headers)
    r = r.json()['beats']
    return prog, r

repeat = 20
C_id = ""
C_sec = ""
AUTH_URL = 'https://accounts.spotify.com/api/token'


auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': C_id,
    'client_secret': C_sec,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}
BASE_URL = 'https://api.spotify.com/v1/'
scope = "user-read-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=C_id,client_secret=C_sec,redirect_uri='http://localhost/',scope=scope,username='s6f2dioy7oy39ps3tfhxmclzg'))
res = sp.current_user_playing_track()
track_id = res['item']['id']
prog = res['progress_ms']/1000
time2 = time.time()
#res['progress_ms']


r = requests.get(BASE_URL + 'audio-analysis/' + track_id, headers=headers)

r = r.json()['tatums']
print(r)
num = 0
bt = True
ser = serial.Serial("COM8", 9600, timeout=1)
time1 = time.time()
while(True):
    if(num+3 >= len(r)):
        num = 0
        prog, r = getdata()
        time2 = time.time()
        time.sleep(1)
        continue
    if(prog+(time.time()-time2)>r[num+1]['start']):
        #print(r[num]['start'], r[num+1]['start'], prog+(time.time()-time2))
        print(r[num+1]['confidence'])
        num += 1
        ser.write(b'trig')
        if bt == True:
            print("beat")
            bt = False
        else:
            print("      boat")
            bt = True
    if(r[num]['start']>prog+(time.time()-time2) or r[num+2]['start']<prog+(time.time()-time2)):
        """first time I felt the need to comment personal work. Sometimes the process time between the conditional above
        and this one sends them over the edge, or rather really often! Thats why I have it check for two events of. This solution feels stupid, and i like it!"""
        print("shit")
        num = findint(r, prog + (time.time() - time2))
        if (num == -1):
            prog, r = getdata()

    if(time.time()>time1+repeat):
        print("checking")
        restemp = sp.current_user_playing_track()
        if(res['item']['id'] != restemp['item']['id']):
            print("called")
            res = sp.current_user_playing_track()
            prog, r = getdata()
            time2 = time.time()
            time1 = time.time()
        else:
            time1 = time.time()



