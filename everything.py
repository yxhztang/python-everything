#coding=utf-8
#使用everything 进行搜索 ....
"""
    将两个脚本 写成一个脚本 :::::
    端口 经常被占用 如下命令帮你解决:
    第一步 tasklist|findstr "2720"  
    第二步 tasklist|findstr "143568
"""
from ctypes import * 
import sys,os
import numpy as np
import cv2
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib import parse
from PIL import Image
from psd_tools import PSDImage

host = ('localhost', 8888)
#定义路径
dll = "F:\\everything64.dll"

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        result = parse.urlparse(self.path)
        dict = parse.parse_qs(result.query)
        #假设存在后缀的部分.....
        if 'method' in dict:
            data = Tool.queryfile(dict['search'][0],dict['is_file'][0],dict['case'][0],dict['path'][0])
        else:
            Tool.image(dict['ext'][0],dict['w'][0],dict['inf'][0],dict['out'][0])
            data = {'result': 'this is a test'}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

#工具类:::
class Tool:
    #文件查询部分 组装数据 文件的详细信息 也要出现:::  #数据太大了 只要2000个
    def queryfile(search,is_file,case,path):
        superSearch=windll.LoadLibrary(dll)
        #文件和文件名 结果:::;
        code = True
        fileList = []
        folderList = []
        if case:
            superSearch.Everything_SetMatchCase(True)
        strBuff=create_unicode_buffer(255) 
        superSearch.Everything_SetSearchW(c_wchar_p(search)) 
        try: 
            superSearch.Everything_QueryW() 
        except Exception as e:
            print( e )
            superSearch.Everything_QueryW(0)
        rsNum=superSearch.Everything_GetNumResults()
        print(search)
        if rsNum==0: 
            print("Everthing not started or files not found!")
        for index in range(0,rsNum): 
            superSearch.Everything_GetResultFullPathNameW(index,byref(strBuff),len(strBuff))
            if int(is_file) > 0:
                if superSearch.Everything_IsFileResult(index):
                    superSearch.Everything_GetResultFullPathNameW(index,byref(strBuff),len(strBuff))
                    name = superSearch.Everything_GetResultFileNameW(index)
                    #size = superSearch.Everything_GetResultSize(index)
                    path = strBuff.value
                    (filepath,tempfilename) = os.path.split(path)
                    (shotname,extension) = os.path.splitext(tempfilename)
                    name = shotname + extension
                    ext = os.path.splitext(path)[1]
                    ext = ext[1:].lower()
                    (size,atime,ctime,mtime) = (0,0,0,0)
                    dict = {'name':name,'path':path,'ext':ext,'type':'file','size':size,'atime':atime,'ctime':ctime,'mtime':mtime}
                    fileList.append(dict)
            else:
                if superSearch.Everything_IsFileResult(index):
                    superSearch.Everything_GetResultFullPathNameW(index,byref(strBuff),len(strBuff))
                    name = superSearch.Everything_GetResultFileNameW(index)
                    #size = superSearch.Everything_GetResultSize(index)
                    path = strBuff.value
                    (filepath,tempfilename) = os.path.split(path)
                    (shotname,extension) = os.path.splitext(tempfilename)
                    name = shotname + extension
                    ext = os.path.splitext(path)[1]
                    ext = ext[1:].lower()
                    (size,atime,ctime,mtime) = (0,0,0,0)
                    dict = {'name':name,'path':path,'ext':ext,'type':'file','size':size,'atime':atime,'ctime':ctime,'mtime':mtime}
                    fileList.append(dict)
                else:
                    superSearch.Everything_GetResultFullPathNameW(index,byref(strBuff),len(strBuff))
                    path = strBuff.value
                    name = os.path.basename(path)
                    dict = {'name':name,'path':path}
                    folderList.append(dict)
        #print(folderList)
        if len(fileList) > 2000:
            fileList = fileList[0:2000]
        if len(folderList) > 2000:
            folderList = folderList[0:2000]
        data = {'fileList':fileList,'folderList':folderList}
        del superSearch 
        del strBuff
        return data


    # 图像处理  部分
    def image(ext,w,inf,out):
        if ext != 'psd':
            img = Image.open(inf)
            if  int(w) < 0:
                size = img.size
                width = size[0]
                height = size[1]
            else:
                width = int(w)
                height = int(w)
            im2 = img.resize((width,height))
            im2 = im2.convert('RGB')
            im2.save(out)
        else:
            psd = PSDImage.load(inf)
            im = psd.as_PIL()
            if int(w) < 0:
                im = im.convert('RGB')
                im.save(out)
            else:
                size = (int(w),int(w))
                im.thumbnail(size, Image.ANTIALIAS)
                im = im.convert('RGB')
                im.save(out)


#进入的接口 >>>>>>>
if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
    #data = Tool.queryfile("E: *设计*",0,0,'E: \\')




