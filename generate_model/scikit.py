import numpy as np
import pandas as pd
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


with open('data\data_10000.json', 'r') as f:
    data = json.load(f)

# 2. 轉換成 DataFrame 格式
df_input = pd.DataFrame([item['input'] for item in data])
df_output = pd.DataFrame([item['output'] for item in data])

# 3. 拆分訓練集與測試集 (80% 訓練, 20% 測試)
X_train, X_test, y_train, y_test = train_test_split(df_input, df_output, test_size=0.2)

# 4. 建立模型並訓練
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# 5. 測試看看準不準
predictions = model.predict(X_test)
error = mean_absolute_error(y_test, predictions)

# 計算百分比誤差
relative_error = np.abs((predictions - y_test.values) / y_test.values) * 100
mean_rel_error = np.mean(relative_error, axis=0)

print(f"--- 物理準確度報告 ---")
print(f"Rv 半徑誤差: {mean_rel_error[0]:.2f}%")
print(f"V2 速度誤差: {mean_rel_error[1]:.2f}%")
print(f"Ms 質量誤差: {mean_rel_error[2]:.2f}%")
joblib.dump(model, 'galaxy_model.joblib')
