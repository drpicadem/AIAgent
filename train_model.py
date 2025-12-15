import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

TARGET_COLUMN = 'hg/ha_yield'
FEATURE_ORDER = ['Area', 'Item', 'Year', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']

NUMERICAL_FEATURES = ['Year', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']
CATEGORICAL_FEATURES = ['Area', 'Item']

print("1. Učitavanje i priprema podataka...")

try:
    df = pd.read_csv('yield_df.csv')
except FileNotFoundError:
    print("GREŠKA: Datoteka 'yield_df.csv' nije pronađena. Provjerite naziv i lokaciju!")
    exit()

df.dropna(inplace=True) 

X = df.drop([TARGET_COLUMN, 'Unnamed: 0'], axis=1)
y = df[TARGET_COLUMN]

X = X[FEATURE_ORDER] 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


print("2. Kreiranje pre-procesora (StandardScaler i OneHotEncoder)...")

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), NUMERICAL_FEATURES),
        ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)
    ],
    remainder='drop' 
)


print("3. Trening Random Forest Regressor modela (AI Agent)...")

model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])

model_pipeline.fit(X_train, y_train)

r2_score = model_pipeline.score(X_test, y_test)
print(f"Model uspješno treniran. R-squared na test setu: {r2_score:.4f}")


print("4. Spremanje agenta (yield_predictor_pipeline.pkl)...")

joblib.dump(model_pipeline, 'yield_predictor_pipeline.pkl')

print("\n---------------------------------------------------------")
print("USPJEH: Model Pipeline je uspješno spremljen!")
print("Spremni ste za pokretanje Flask API-ja (`python app.py`).")
print("---------------------------------------------------------")