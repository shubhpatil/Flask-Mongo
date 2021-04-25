from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import xmltodict
import os
import cv2
import time

client = MongoClient('mongodb+srv://unknown:unknown@student.gb0wa.mongodb.net/baggage?retryWrites=true&w=majority')
db = client['baggage']
collection = db['reports']

app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET'])
def index():
    dbdata = collection.find_one({})
    print(dbdata)
    return jsonify({"message": "Hello python flask"})

@app.route('/output/<path:path>')
def send_js(path):
    return send_from_directory('output', path)

@app.route("/detection", methods=['POST'])
def detection():
    imageFile = request.files['image']
    xmlFile = request.files['xml']

    imageFile.save(imageFile.filename)  
    # xmlFile.save(xmlFile.filename) 

    xmlData = parseXML(xmlFile, imageFile.filename)
    return jsonify({"message": "Upload Success", "xmlData": xmlData})

def parseXML(xmlFile, imageName):
    xmlData = xmltodict.parse(xmlFile)
    objects = xmlData['annotation']['object']
    isArr = isinstance(objects, list)
    imageProcessing(objects, imageName, isArr)
    return objects

def imageProcessing(objects, imageName, isArr):
    path = os.path.dirname(os.path.abspath(imageName))
    outputPath = path + '\output'
    path = path + f"\{imageName}"
    image = cv2.imread(path)
    if (isArr == True):
        for obj in objects:
            imageOperation(image, obj, imageName)
    else:
        imageOperation(image, objects, imageName)
    cv2.imwrite(os.path.join(outputPath , imageName), image)

def imageOperation(image, obj, imageName):
    x1 = int(obj['bndbox']['xmin']) 
    y1 = int(obj['bndbox']['ymin'])
    x2 = int(obj['bndbox']['xmax'])
    y2 = int(obj['bndbox']['ymax'])
    objectName = obj['name']
    cv2.putText(image, objectName, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    dbProcess(imageName, objectName, x1, y1, x2, y2)

def dbProcess(imageName, objectName, x1, y1, x2, y2):
    timestamp = time.time()
    report = { "image": imageName, "object": objectName, "xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2, "timestamp": timestamp }
    collection.insert_one(report)
    
if __name__ == "__main__":
    app.run(debug=True);