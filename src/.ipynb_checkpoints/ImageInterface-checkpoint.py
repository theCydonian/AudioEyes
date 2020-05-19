import cv2
import numpy as np
from PIL import Image
import pytesseract as pts
from spellchecker import SpellChecker
import requests
import os

class ImageInterface:
    """Class Description"""
    
    def __init__(self):
        self.calibrated = False
        self.objpoints = []
        self.imgpoints = []
        self.spell = SpellChecker()
    
    def calibrate(self, img_list):
        if len(img_list) == 0:
            return 'Sorry, please try again with calibration images.'
        
        self.objpoints = []
        self.imgpoints = []
        
        objp = np.zeros((6*9,3), np.float32)
        objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)
        
        for img in img_list:
            grey = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(grey, (9,6),None)
            if ret == True:
                self.objpoints.append(objp)
                self.imgpoints.append(corners)
        
        self.calibrated = True
        return 'Successful Calibration!'
    
    def undistort(self, img):
        if self.calibrated:
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, img.shape[1:], None, None)
            undist = cv2.undistort(img, mtx, dist, None, mtx)
            return undist
        else:
            return img
    
    def find_corners(self, img):
        grey = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        min_dist = 1000
        min_quality = 0.1
        
        corners = cv2.goodFeaturesToTrack(grey, 4, min_quality, min_dist)
        
        return corners
    
    def get_alignment(self, img):
        dark_threshold = 100
        margin = 5
        
        undist = self.undistort(img)
        grey = cv2.cvtColor(undist,cv2.COLOR_BGR2GRAY)
        
        vertical_med = [np.median(row) for row in grey]
        
        transpose = cv2.transpose(grey)
        horizontal_med = [np.median(col) for col in transpose]
    
        top = np.mean(vertical_med[0:margin]) > dark_threshold
        bottom = np.mean(vertical_med[-1-margin:-1]) > dark_threshold
        left = np.mean(horizontal_med[0:margin]) > dark_threshold
        right = np.mean(horizontal_med[-1-margin:-1]) > dark_threshold
        
        if top and bottom or left and right:
            return "Object is too large, reposition camera, or proceed with caution", vertical_med, horizontal_med, grey
        elif top and left:
            return "Move object down and to the right", vertical_med, horizontal_med, grey
        elif top and right:
            return "Move object down and to the left", vertical_med, horizontal_med, grey
        elif top:
            return "Move object down", vertical_med, horizontal_med, grey
        elif bottom and left:
            return "Move object up and to the right", vertical_med, horizontal_med, grey
        elif bottom and right:
            return "Move object up and to the left", vertical_med, horizontal_med, grey
        elif bottom:
            return "Move object up", vertical_med, horizontal_med, grey
        elif left:
            return "Move object right", vertical_med, horizontal_med, grey
        elif right:
            return "Move object left", vertical_med, horizontal_med, grey
        return "You have successfully placed the object!", vertical_med, horizontal_med, grey
    
    def get_text(self, img):
        grey = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        undist = self.undistort(grey)
        text = pts.image_to_string(Image.fromarray(undist), lang='eng')
        
        words = self.spell.split_words(text)
        percentEnglish = (1-len(self.spell.unknown(words))/len(words))*100
        
        return [phrase for phrase in text.split('\n')
                if phrase is not '\x0c'
                and phrase is not ''
                and phrase is not ' '], percentEnglish
    
    def send_to_workers(self, img, contract, account, server='http://127.0.0.1:8000/upload'):
        cv2.imwrite('../img_cache/img.png', img)
        
        data = open('../img_cache/img.png' ,'rb')
        print(data)
        r = requests.post(server, data=data)
        
        out = os.popen('near call ' + contract + ' req_transcription ' + '\'{"img": "' + r.text + '"}\'' + ' --account-id ' + account), r.text
        return out
    
    def get_solved(self, img_hash, contract, account):
        out = os.popen('near view ' + contract + ' get_transcription ' + '\'{"img": "' + img_hash + '"}\'' + ' --account-id ' + account).read()
        os.system('near view ' + contract + ' rem_transcription ' + '\'{"img": "' + img_hash + '"}\'' + ' --account-id ' + account)
        return [item[1:] for item in out.split('\n')[-2][1:-1].replace('\'','').replace('\\n', '\n').replace('\x1b[32m', '').replace('\x1b[39m', '').split(',')[0:2]]
    
    def tip(self, user, amount, contract, account):
        out = os.popen('near call ' + contract + ' send_tip ' + '\'{"account_id": "' + user + '"}\'' + ' --account-id ' + account + ' --amount ' + amount)
        return out