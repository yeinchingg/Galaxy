from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib  
import numpy as np
import pandas as pd
app = Flask(__name__)
CORS(app)  # 允許網頁跨網域存取

# 載入你訓練好的模型
model = joblib.load('galaxy_model.joblib')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_data = pd.DataFrame([{
        'logM': data['logM'],
        'rd': data['rd'],
        'sfr': data['sfr']
    }])
    pred = model.predict(input_data)[0]
    return jsonify({
        "Rv": float(pred[0]),
        "V2": float(pred[1]),
        "Ms": float(pred[2]),
        "ai_distort": float(np.random.uniform(0.1, 0.4)),  # 暫時用隨機，之後可由 AI 預測
        "glow_size": float(1.2 + data['sfr'] * 0.1)      # 讓光暈跟著 SFR 連動
    })
 

if __name__ == '__main__':
    app.run(port=5000)
