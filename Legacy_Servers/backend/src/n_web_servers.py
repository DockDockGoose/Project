from web_server import webServer
import numpy as np
import os
import sys
import subprocess
#from subprocess import call
SERV_HOST_NAME  = '127.0.0.1'
N = 1

class createWebServers():

  def __init__(self, num=N):
    curr = 65000
    for i in np.arange(0, N):
      #osString = "start cmd /k python3 web_server.py localhost " + str(curr)
      #print(osString)
      osString = "python3 web_server.py localhost " + str(curr)
      subprocess.Popen(osString, shell=True)
      curr = curr + 1
      #os.system(osString)

if __name__ == '__main__':
  if(len(sys.argv) < 2): 
    N = int(input("How many web servers would you like created? (Default 1): ") or 1)
  else:
    N = int(sys.argv[1])
  createWebServers(N)
