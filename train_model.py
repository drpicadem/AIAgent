import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

# --- 1. DEFINICIJA VARIJABLI (SINKRONIZACIJA S app.py) ---
# OVE LISTE DEFINIRAJU STRUKTURU VASEG DATASETA yield_df.csv
TARGET_COLUMN = 'hg/ha_yield'
FEATURE_ORDER = ['Area', 'Item', 'Year', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']

# Definiranje tipova značajki za preprocesor
NUMERICAL_FEATURES = ['Year', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']
CATEGORICAL_FEATURES = ['Area', 'Item']

# --- 2. Učitavanje i Priprema Podataka ---
print("1. Učitavanje i priprema podataka...")

try:
    df = pd.read_csv('yield_df.csv')
except FileNotFoundError:
    print("GREŠKA: Datoteka 'yield_df.csv' nije pronađena. Provjerite naziv i lokaciju!")
    exit()

# Rješavanje nedostajućih vrijednosti (iako je set čist, dobra praksa je zadržati)
# Drop missing values for simplicity in this project
df.dropna(inplace=True) 

# Izbacivanje suvišnog (indeks) i ciljne kolone za X
X = df.drop([TARGET_COLUMN, 'Unnamed: 0'], axis=1)
y = df[TARGET_COLUMN]

# KLJUČNA SINKRONIZACIJA: Osiguravamo da X ima redoslijed kolona identičan FEATURE_ORDER listi
X = X[FEATURE_ORDER] 

# Podjela na trening i test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# --- 3. Kreiranje Pre-procesora ---
print("2. Kreiranje pre-procesora (StandardScaler i OneHotEncoder)...")

preprocessor = ColumnTransformer(
    transformers=[
        # Skaliranje za numeričke podatke
        ('num', StandardScaler(), NUMERICAL_FEATURES),
        # Kodiranje za kategorijske podatke (handle_unknown='ignore' sprječava crash na nepoznatim vrijednostima)
        ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)
    ],
    remainder='drop' # Izbacujemo sve ostale kolone koje nisu definirane
)


# --- 4. Trening Modela (Pipeline) ---
print("3. Trening Random Forest Regressor modela (AI Agent)...")

# Pipeline: Prvo pre-procesiraj, zatim treniraj model
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])

# Trening
model_pipeline.fit(X_train, y_train)

# Evaluacija (provjera uspješnosti modela)
r2_score = model_pipeline.score(X_test, y_test)
print(f"Model uspješno treniran. R-squared na test setu: {r2_score:.4f}")


# --- 5. Spremanje Agent-a (Pipeline) ---
print("4. Spremanje agenta (yield_predictor_pipeline.pkl)...")

# Spremanje cijelog Pipeline objekta
joblib.dump(model_pipeline, 'yield_predictor_pipeline.pkl')

print("\n---------------------------------------------------------")
print("USPJEH: Model Pipeline je uspješno spremljen!")
print("Spremni ste za pokretanje Flask API-ja (`python app.py`).")
print("---------------------------------------------------------")