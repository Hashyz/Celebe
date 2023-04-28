import random,time
import requests
import json
from urllib3.exceptions import InsecureRequestWarning#InsecureRequestWarning
from requests.adapters import HTTPAdapter, Retry#Retry Connection retired
import urllib3
urllib3.disable_warnings(InsecureRequestWarning)
class Celebe:
  def __init__(self):
    self.lat = ''.join(random.choices('0123456789', k=6))
    self.lng = ''.join(random.choices('0123456789', k=6))
    self.init_userAgent()

    self.session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    self.session.mount('http://', adapter)
    self.session.mount('https://', adapter)

  def init_userAgent(self):
    self.phone = random.choice(["MI 5X","SM-A037U","RMX3085","SM-A536E","M2006C3LG","CPH2099","NTH-NX9","CPH2099"])
    self.mobi_headers = f"Mozilla/5.0 (Linux; Android 7.1.2; {self.phone}; Flow) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/347.0.0.268 Mobile Safari/537.36"

  def getToken(self,rfToken,output=False):
    self.refreshToken = rfToken
    
    refresh_header = {
        "Content-Type": "application/json",
        "X-Android-Package": "io.celebe.th",
        "X-Android-Cert": "A248506845AFFBB22EFA06817ED72D0A85C9C9D0",
        "X-Client-Version": "Android/Fallback/X21000008/FirebaseCore-Android",
        "User-Agent": self.mobi_headers,
        "Host": "securetoken.googleapis.com",
    }
    data = {"grantType": "refresh_token", "refreshToken": self.refreshToken}
    response = self.session.post(
                            "https://securetoken.googleapis.com/v1/token?key=AIzaSyB9Bs3mibiSfPpP23sESgl_Tt2_4mjSSoA",
                            headers=refresh_header,
                            json=data,
                            verify=False,
                            )
    account = response.content.decode("utf-8")
    self.token = json.loads(account)["access_token"]
    # uid = json.loads(account)["user_id"]
    if output:
      print(self.token)
    # project = json.loads(account)["project_id"]

  def setToken(self,token):
    self.token = token

  def getUser(self):
    url = 'https://api-th.celebe.io/auth/v1/users'
    self.headers = {
        'Host': 'api-th.celebe.io',
        'accept': 'application/json, text/plain, */*',
        'platform': 'android',
        'version': '2.1.0',
        'region': 'TH',
        'device': self.phone,
        'profile-id': '0',
        'content-type': 'application/json',
        'x-access-token': self.token,
        'user-agent': 'okhttp/4.9.0',
        'coordinate': f'lat:31.{self.lat};lng:121.{self.lng}'
    }
    data = '{"nickname":"USER_CREATE_FIREBASE_ONLY"}'
    response = requests.post(url, headers=self.headers, data=data, verify=False)
    if response.status_code == 200:
      self.poid = response.json()['body']
    else:
      return response
      # self.getUser()

  def login(self,output=True):
    url = 'https://api-th.celebe.io/auth/v1/users/login'
    self.headers['profile-id'] = str(self.poid)
    response = self.session.get(url, headers=self.headers, verify=False)
    account = response.content
    self.account = account
    ppid1 = json.loads(account)['body']['id']
    name = json.loads(account)['body']['name']
    if output:
      print(f'Name : {name} | id : {ppid1}')

  def getRecommend(self):
    url = "https://api.celebe.io/resource/v1/feeds/recommend?pageNo=1"
    self.session.get(url,headers=self.headers, verify=False)
    url2 = "https://api.celebe.io/resource/v1/feeds/recent?pageNo=1"
    res = self.session.get(url2,headers=self.headers, verify=False)
    # self.j = res.json()
    for post in res.json()['body']:
      oID = post['profile']['id']
      lv = post['profile']['type']
      nick = post['profile']['nickname']
      print(f"Post User : {nick} | Lv : {lv} | id : {oID}")
      self.viewVideo(oID)

  def viewVideo(self,pid):##
    noT = 1
    for no in range(1,15):
      response = self.session.get(f'https://api-th.celebe.io/resource/v1/feeds/profile/{pid}/type/VIDEO?pageNo={no}', headers=self.headers, verify=False)
      if response.status_code == 200:
        accounts = response.json()
        body = accounts['body']
        print(f"Total Post in Page {no}: {len(body)}")

        for post in body:
          vid = post['videoUrl'].split('/')[-2]#post['videoUrl']
          viewc = post['readCount']
          vtime = post['videoRunningTime']
          print(f'Video ID : {vid} - {viewc} views - {vtime}s')

          view_url = f"https://api-th.celebe.io/resource/v1/feeds/{vid}/view"

          data = {"viewTime": vtime*1000}

          response = self.session.post(view_url, headers=self.headers, json=data, verify=False)
          if response.status_code == 200:
            succ = response.json().get('header')
            if succ != None:
              if succ.get('isSuccessful'):
                print(f"{noT}. OK!")
          time.sleep(3)
          noT+=1
      else:
        print("Error :3")
        return 0
    return 1
    
obj = Celebe()
while 1:
  k = input("Refresh Token (r) or Token (t) : ").lower()
  if k == 'r':
    refreshToken = input("Refresh Token : ")
    obj.getToken(refreshToken)
    break
  elif k == 't':
    r = input("Token : ")
    obj.setToken(r)
    break
  else:
    print("Just Choose r or t.")

obj.getUser()
obj.login()

while 1:
  opt = input("Option (a) - Profile id - \nOption (b) - View All Recommend Video -\nInput here : ").lower()
  if opt == 'a':
    obj.viewVideo(input("Profile ID Here : "))#382844
    # break
  elif opt == 'b':
    obj.getRecommend()
    # break
  else:
    print("Just Choose a or b.")
