from tkinter import S
from pickle import GET
from unittest import result
from flask import Flask, request, jsonify  
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from 
import pandas as pd
import re
from unidecode import unidecode
import sqlite3


app = Flask(__name__)

app.json_encoder = LazyJSONEncoder

swagger_template = dict(
info = {
    'title': LazyString(lambda: 'Cleansing API untuk CSV dan JSON '),
    'version': LazyString(lambda: '1'),
    'description': LazyString(lambda: 'Challange Gold'),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)

def _remove_more(s):
    s = re.sub(r"\\x[A-Za-z0-9./]+"," ",unidecode(s))
    return s

def _remove_more_word(s):
    s = s.strip().replace(r"\n", " ")
    return s

def _remove_punct(s):
    s = re.sub(r"[^\w\d\s]+", " ", s)
    return s


@swag_from("swagger_config_post.yml", methods=['POST'])
@app.route("/upload_text/v1", methods=["POST"])
def remove_punct_text():
    s = request.get_json()
    result = _remove_more(s['text'])
    result = _remove_more_word(result)
    result = _remove_punct(result)
    conn = sqlite3.connect("challange_binar.db")
    conn.execute("insert into text_tweet (dirty_tweet, clean_tweet) values (?,?)", (s['text'], result))
    conn.commit()
    conn.close()

    
    return jsonify({"hasil_bersih": (result)})



@swag_from("swagger_config_file.yml", methods=['POST'])
@app.route("/upload_csv/v1", methods=["POST"])
def remove_punct_emoji():
    file = request.files["files"]
    df = pd.read_csv(file, encoding='ISO-8859-1')
    df['new_tweet'] = df['Tweet']
    df['new_tweet'] = df['new_tweet'].apply(_remove_more)
    df['new_tweet'] = df['new_tweet'].apply(_remove_more_word)
    df['new_tweet'] = df['new_tweet'].apply(_remove_punct)
    conn = sqlite3.connect("challange_binar.db")
    df.to_sql('text_tweet3', con=conn, index=False, if_exists='append')

   
    print(df.head(10))
    return jsonify({"Upload":"berhasil"})


if __name__ == "__main__": 
    app.run(port=5000, debug=True)


