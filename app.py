from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import requests  # <--- NOVO: Za dohvaćanje podataka s interneta

app = Flask(__name__, static_url_path='', static_folder='static')
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

# --- KONFIGURACIJA ---
DATASET_NAME = 'yield_df.csv'
MODEL_FILE = 'yield_predictor_pipeline.pkl'
FEATURE_ORDER = ['Area', 'Item', 'Year', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']

# --- GLOBALNE VARIJABLE ---
MODEL_PIPELINE = None
DF_META = None
UNIQUE_AREAS = []
UNIQUE_ITEMS = []
COUNTRY_STATS = {}
MODEL_TRAINED = False

# --- UČITAVANJE PODATAKA ---
try:
    print("⏳ Pokrećem server...")
    
    # Provjeri da li postoji već istreniran model
    import os
    if os.path.exists(MODEL_FILE):
        MODEL_PIPELINE = joblib.load(MODEL_FILE)
        MODEL_TRAINED = True
        print(f"✅ Pronađen postojeći model - učitan i spreman!")
    else:
        print(f"ℹ️ Model fajl ne postoji - korisnik mora kliknuti 'Istreniraj Model'!")
    
    DF_META = pd.read_csv(DATASET_NAME)
    
    DF_META['Area'] = DF_META['Area'].astype(str).str.strip()
    DF_META['Item'] = DF_META['Item'].astype(str).str.strip()
    
    UNIQUE_AREAS = sorted(list(set(DF_META['Area'].dropna().tolist())))
    UNIQUE_ITEMS = sorted(list(set(DF_META['Item'].dropna().tolist())))

    # Statistika za "Pametne prosjeke" (Backup ako nema interneta)
    stats_df = DF_META.groupby('Area')[['average_rain_fall_mm_per_year', 'avg_temp', 'pesticides_tonnes']].mean()
    COUNTRY_STATS = stats_df.to_dict('index')
    
    print(f"✅ Podaci učitani. Status: MODEL_TRAINED = {MODEL_TRAINED}")

except Exception as e:
    print(f"❌ GREŠKA: {e}")

# --- RUTE ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_metadata', methods=['GET'])
def get_metadata():
    if not UNIQUE_AREAS: return jsonify({'error': 'Greška u podacima.'}), 500
    return jsonify({'status': 'success', 'areas': UNIQUE_AREAS, 'items': UNIQUE_ITEMS, 'country_stats': COUNTRY_STATS, 'model_trained': MODEL_TRAINED})

@app.route('/model_status', methods=['GET'])
def model_status():
    """Provjerava da li je model treniran"""
    return jsonify({'model_trained': MODEL_TRAINED})

@app.route('/train_model', methods=['POST'])
def train_model():
    """Trenira model na zahtjev korisnika"""
    global MODEL_PIPELINE, MODEL_TRAINED
    
    try:
        print("🔄 Započinjem treniranje modela...")
        
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler, OneHotEncoder
        from sklearn.model_selection import train_test_split
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        
        # Priprema podataka
        df = DF_META.copy()
        df.dropna(inplace=True)
        
        TARGET_COLUMN = 'hg/ha_yield'
        X = df[FEATURE_ORDER]
        y = df[TARGET_COLUMN]
        
        # Podjela podataka
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Definiranje tipova značajki
        NUMERICAL_FEATURES = ['Year', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']
        CATEGORICAL_FEATURES = ['Area', 'Item']
        
        # Kreiranje preprocessora
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), NUMERICAL_FEATURES),
                ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)
            ],
            remainder='drop'
        )
        
        # Kreiranje i treniranje pipeline-a
        MODEL_PIPELINE = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
        ])
        
        MODEL_PIPELINE.fit(X_train, y_train)
        
        # Evaluacija
        r2_score = MODEL_PIPELINE.score(X_test, y_test)
        
        # Spremanje modela
        joblib.dump(MODEL_PIPELINE, MODEL_FILE)
        
        MODEL_TRAINED = True
        
        print(f"✅ Model uspješno treniran! R² score: {r2_score:.4f}")
        
        return jsonify({
            'status': 'success',
            'message': 'Model uspješno treniran!',
            'r2_score': round(r2_score, 4),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        })
        
    except Exception as e:
        print(f"❌ Greška pri treniranju: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/save_data', methods=['POST', 'OPTIONS'], strict_slashes=False)
def save_data():
    # Rješava CORS preflight
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()

        new_row = {
            'Area': data['Area'],
            'Item': data['Item'],
            'Year': data['Year'],
            'hg/ha_yield': data['predicted_yield'] * 10,
            'average_rain_fall_mm_per_year': data['average_rain_fall_mm_per_year'],
            'pesticides_tonnes': data['pesticides_tonnes'],
            'avg_temp': data['avg_temp']
        }

        df = pd.read_csv(DATASET_NAME)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATASET_NAME, index=False)

        global DF_META
        DF_META = df
        DF_META['Area'] = DF_META['Area'].astype(str).str.strip()
        DF_META['Item'] = DF_META['Item'].astype(str).str.strip()

        print(f"✅ Podaci spremljeni u {DATASET_NAME}")

        return jsonify({'status': 'success', 'message': 'Podaci uspješno spremljeni u CSV!'})

    except Exception as e:
        print(f"❌ Greška pri spremanju: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


# --- NOVO: RUTA ZA VREMENSKU PROGNOZU UŽIVO ---
@app.route('/get_live_weather', methods=['POST'])
def get_live_weather():
    """
    1. Prima ime države.
    2. Traži koordinate (Lat/Lon) preko Geocoding API-ja.
    3. Traži temperaturu i kišu preko Weather API-ja.
    """
    try:
        data = request.get_json()
        country = data.get('country')
        
        if not country:
            return jsonify({'error': 'Nije odabrana država'}), 400

        # 1. Geocoding (Tražimo koordinate države)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={country}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get('results'):
            return jsonify({'error': 'Nisam uspio pronaći koordinate za ovu državu.'}), 404
            
        lat = geo_res['results'][0]['latitude']
        lon = geo_res['results'][0]['longitude']

        # 2. Weather (Tražimo trenutno vrijeme)
        # Tražimo trenutnu temperaturu i sumu kiše u zadnjih 7 dana (kao procjenu vlažnosti)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&daily=rain_sum&timezone=auto"
        weather_res = requests.get(weather_url).json()
        
        current_temp = weather_res['current']['temperature_2m']
        
        # Za kišu je teško dobiti "godišnji prosjek" iz trenutnog vremena.
        # Zato ćemo uzeti "Pametni prosjek" iz našeg CSV-a.
        historical_avg_rain = COUNTRY_STATS.get(country, {}).get('average_rain_fall_mm_per_year', 1000)
        
        return jsonify({
            'status': 'success',
            'temp': current_temp,
            'rain': historical_avg_rain,
            'lat': lat,
            'lon': lon,
            'note': f"Dohvaćeno s lokacije: {geo_res['results'][0]['name']}"
        })

    except Exception as e:
        print(f"Weather API Greška: {e}")
        return jsonify({'error': 'Ne mogu dohvatiti vremensku prognozu.'}), 500

@app.route('/predict_yield', methods=['POST'])
def predict_yield():
    if not MODEL_TRAINED or MODEL_PIPELINE is None: 
        return jsonify({'error': 'Model nije treniran. Molim kliknite "Istreniraj Model" prvo.'}), 400

    try:
        data = request.get_json(force=True)
        input_data = {col: [data[col]] for col in FEATURE_ORDER}
        input_df = pd.DataFrame(input_data)
        
        prediction = MODEL_PIPELINE.predict(input_df)
        predicted_yield_kg_ha = round(prediction[0] / 10, 2)

        history = DF_META[
            (DF_META['Area'] == data['Area']) & 
            (DF_META['Item'] == data['Item'])
        ].sort_values(by='Year').tail(10)

        if history.empty:
            return jsonify({
                'status': 'no_data',
                'message': f"Nažalost, nemamo povijesnih podataka za {data['Item']} u državi {data['Area']}. Nemoguće izračunati prinos."
            })

        return jsonify({
            'status': 'success',
            'predicted_yield_kg_ha': predicted_yield_kg_ha,
            'unit': 'kg/ha',
            'details': f"{data['Item']} ({data['Area']})",
            'history_years': history['Year'].tolist(),
            'history_yields': [round(y/10, 2) for y in history['hg/ha_yield'].tolist()],
            'prediction_year': data['Year']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(
        port=5000,
        debug=False,
        use_reloader=False
    )
