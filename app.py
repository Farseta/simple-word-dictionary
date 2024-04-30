from flask import Flask, request, render_template,redirect, jsonify,url_for
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)


@app.route('/')
def index():
    word_result = db.words.find({},{"_id":False})
    words=[]
    for word in word_result:
        definiton = word["definitions"][0]["shortdef"]
        definiton = definiton if type(definiton) is str else definiton[0]
        words.append({
            "word":word["word"],
            "definiton":definiton,

        })
    msg = request.args.get('msg')
    return render_template('index.html' , Words = words, Msg=msg)

@app.route("/detail/<keyword>")
def detail(keyword):
    print(keyword)
    api_key = "36454664-87d4-4094-9605-48ffd7241ab1"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response=requests.get(url)
    definitions = response.json()
    
    if not definitions or type(definitions[0]) is str:
        return redirect(url_for(
            'handle_error',
            
            keyword = keyword
        ))
    
        
    
    status = request.args.get("status_give", "new")
    return render_template( "detail.html", word = keyword, Definitions = definitions, Status = status)

@app.route("/api/save_word",methods=["POST"])
def save_word():
    jsnon_Data = request.get_json()
    word = jsnon_Data.get('word_give')
    definitions = jsnon_Data.get('definitions_give')
    
    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y-%m-%d'),
    }
    db.words.insert_one(doc)
    
    return jsonify({
        "result":"success",
        "msg":f'the word, {word}, was saved successfully',
    })
    
@app.route("/api/delete_word",methods=["POST"])
def delete_word():
    word = request.form.get("word_give")
    db.words.delete_one({'word':word})
    db.examples.delete_many({'word':word})
    return jsonify({
        "result":"success",
        "msg":f'{word} deleted successfully',
    })
    
@app.route("/handle_error/<keyword>",methods=["POST","GET"])
def handle_error(keyword):
    #dictionary initiation
    api_key = "36454664-87d4-4094-9605-48ffd7241ab1"
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response=requests.get(url)
    definitions = response.json()
    #database initiation
    word_result = db.words.find({},{"_id":False})
    words=[]
    for word in word_result:
        definiton = word["definitions"][0]["shortdef"]
        definiton = definiton if type(definiton) is str else definiton[0]
        words.append({
            "word":word["word"],
        })
    
    
    if not definitions:
        print("with no suggestions")
        msg = f"Sorry, we couldn't find the word '{keyword}' in the dictionary. Please check the word and try again."
        return render_template("handle_error.html",Msg = msg)
    if type(definitions[0]) is str:
        suggesion=[]
        
        for denfinition in definitions:
            print(word["word"] == denfinition)
            many = len(words)-1
            count =0
            
            
            for word in words:
                
                if word["word"] == denfinition: 
                    suggesion.append({
                        "definiton" : denfinition,
                        "status":"?status_give=old"
                        
                    })
                    break
                else:
                    if count == many:
                        suggesion.append({
                        "definiton" : denfinition,
                        "status":"?status_give=new"})
                count = count + 1
                #print(count)
                        
                        
                    
                 
        print("with suggestions")
        msg = f"Sorry, we couldn't find the word '{keyword}' in the dictionary. maybe you mean :"
        return render_template("handle_error.html",Suggesion =suggesion,Msg = msg)
    return render_template("handle_error.html")
#example
@app.route("/api/gets_exs",methods=["GET"])
def get_exs():
    word = request.args.get("word")
    example_data = db.examples.find({'word':word})
    examples=[]
    for example in example_data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get('_id')),
        })
    return jsonify({'result':"success",'examples': examples})

@app.route("/api/save_ex", methods=["POST"])
def save_ex():
    word = request.form.get("word")
    example = request.form.get("example")
    doc = {
        'word': word,
        'example': example,
    }
    db.examples.insert_one(doc)
    return jsonify({
        'result':"success",
        'msg': f'your example for the word,{example},for the word, {word}, was saved!',
        })
    
@app.route("/api/delete_ex", methods=["POST"])
def delete_ex():
    id = request.form.get("id")
    word = request.form.get("word")
    db.examples.delete_one({'_id': ObjectId(id)})
    return jsonify({'result':"success", 'msg':f'your example for word,{word}, was deleted!',})


if __name__ == '__main__':
    app.run("0.0.0.0",port=5000,debug=True)
