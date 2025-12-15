from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import requests
import os

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATASET_NAME = os.path.join(DATA_DIR, 'yield_df.csv')
MODEL_FILE = os.path.join(BASE_DIR, 'yield_predictor_pipeline.pkl')

FEATURE_ORDER = ['Area', 'Item', 'Year', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp', 'drought_index']


MODEL_PIPELINE = None
DF_META = None
UNIQUE_AREAS = []
UNIQUE_ITEMS = []
COUNTRY_STATS = {}
MODEL_TRAINED = False



def inspect_csv():
    """Učitava CSV bez ispisivanja debug informacija u terminal"""
    if not os.path.exists(DATASET_NAME):
        return None

    try:
        df = pd.read_csv(DATASET_NAME)
    
        required_cols = [col for col in FEATURE_ORDER if col != 'drought_index']
        
        if 'hg/ha_yield' not in df.columns:
            required_cols.append('hg/ha_yield')

        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            return None
            
        return df
    except Exception:
        return None

def load_data_initial():
    global DF_META, UNIQUE_AREAS, UNIQUE_ITEMS, COUNTRY_STATS, MODEL_PIPELINE, MODEL_TRAINED
    try:
        df = inspect_csv()
        
        if df is None or df.empty:
            DF_META = pd.DataFrame(columns=FEATURE_ORDER + ['hg/ha_yield'])
        else:
            if not df.empty and 'average_rain_fall_mm_per_year' in df.columns and 'avg_temp' in df.columns:
                 df['drought_index'] = df['average_rain_fall_mm_per_year'] / (df['avg_temp'] + 20)
            
            DF_META = df

        if not DF_META.empty:
            if 'Area' in DF_META.columns: DF_META['Area'] = DF_META['Area'].astype(str).str.strip()
            if 'Item' in DF_META.columns: DF_META['Item'] = DF_META['Item'].astype(str).str.strip()
            
            UNIQUE_AREAS = sorted(list(set(DF_META['Area'].dropna().tolist())))
            UNIQUE_ITEMS = sorted(list(set(DF_META['Item'].dropna().tolist())))
            
            try:
                stats_df = DF_META.groupby('Area')[['average_rain_fall_mm_per_year', 'avg_temp', 'pesticides_tonnes']].mean()
                COUNTRY_STATS = stats_df.to_dict('index')
            except KeyError:
                pass

        if os.path.exists(MODEL_FILE):
            try:
                MODEL_PIPELINE = joblib.load(MODEL_FILE)
                MODEL_TRAINED = True
            except:
                MODEL_TRAINED = False
        else:
            MODEL_TRAINED = False

    except Exception:
        pass

load_data_initial()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_metadata', methods=['GET'])
def get_metadata():
    return jsonify({
        'status': 'success', 
        'areas': UNIQUE_AREAS, 
        'items': UNIQUE_ITEMS, 
        'country_stats': COUNTRY_STATS, 
        'model_trained': MODEL_TRAINED
    })

@app.route('/model_status', methods=['GET'])
def model_status():
    return jsonify({'model_trained': MODEL_TRAINED})

@app.route('/train_model', methods=['POST'])
def train_model():
    global MODEL_PIPELINE, MODEL_TRAINED, DF_META
    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler, OneHotEncoder
        from sklearn.model_selection import train_test_split
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        
        df = inspect_csv()
        if df is None or len(df) < 5:
            return jsonify({'status': 'error', 'error': 'CSV fajl nije pronađen ili ima manje od 5 redova!'}), 400
            
        df.dropna(inplace=True)
        
        df['drought_index'] = df['average_rain_fall_mm_per_year'] / (df['avg_temp'] + 20)
        
        if 'hg/ha_yield' not in df.columns:
             return jsonify({'status': 'error', 'error': 'U CSV-u fali kolona "hg/ha_yield" (ciljna varijabla)!'}), 400

        X = df[FEATURE_ORDER]
        y = df['hg/ha_yield']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), ['Year', 'average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp', 'drought_index']),
                ('cat', OneHotEncoder(handle_unknown='ignore'), ['Area', 'Item'])
            ], remainder='drop'
        )
        
        MODEL_PIPELINE = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
        ])
        
        MODEL_PIPELINE.fit(X_train, y_train)
        r2_score = MODEL_PIPELINE.score(X_test, y_test)
        
        joblib.dump(MODEL_PIPELINE, MODEL_FILE)
        MODEL_TRAINED = True
        DF_META = df
        
        return jsonify({'status': 'success', 'r2_score': round(r2_score, 4)})
        
    except Exception as e:
        print(f"❌ GREŠKA PRI TRENIRANJU: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/save_data', methods=['POST'])
def save_data():
    global DF_META
    try:
        data = request.get_json()
        
        if os.path.exists(DATASET_NAME):
            df = pd.read_csv(DATASET_NAME)
        else:
            df = pd.DataFrame(columns=FEATURE_ORDER + ['hg/ha_yield'])

        duplicate_check = df[
            (df['Area'].astype(str) == str(data['Area'])) & 
            (df['Item'].astype(str) == str(data['Item'])) & 
            (df['Year'].astype(int) == int(data['Year']))
        ]

        if not duplicate_check.empty:
            print(f"⚠️ NIJE MOGUĆ UPIS U CSV: Podaci za {data['Year']} ({data['Item']} - {data['Area']}) već postoje.")
            return jsonify({
                'status': 'error', 
                'error': f"Podaci za {data['Year']}. godinu ({data['Item']}) u državi {data['Area']} već postoje!"
            }), 400

        new_row = {
            'Area': data['Area'],
            'Item': data['Item'],
            'Year': data['Year'],
            'hg/ha_yield': float(data['predicted_yield']) * 10,
            'average_rain_fall_mm_per_year': data['average_rain_fall_mm_per_year'],
            'pesticides_tonnes': data['pesticides_tonnes'],
            'avg_temp': data['avg_temp']
        }

        df_new = pd.DataFrame([new_row])
        
        df = pd.concat([df, df_new], ignore_index=True)
        df.to_csv(DATASET_NAME, index=False)
        
        DF_META = df 
        
        return jsonify({'status': 'success', 'message': 'Podaci uspješno spremljeni!'})

    except Exception as e:
        print(f"❌ Greška pri spremanju: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500
    
@app.route('/get_live_weather', methods=['POST'])
def get_live_weather():
    try:
        data = request.get_json()
        country = data.get('country')
        if not country: return jsonify({'error': 'Nije odabrana država'}), 400

        geo_res = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={country}&count=1&language=en&format=json", timeout=5).json()
        if not geo_res.get('results'): return jsonify({'error': 'Nepoznata država'}), 404
            
        lat = geo_res['results'][0]['latitude']
        lon = geo_res['results'][0]['longitude']
        weather_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&timezone=auto", timeout=5).json()
        
        return jsonify({'status': 'success', 'temp': weather_res['current']['temperature_2m'], 'note': geo_res['results'][0]['name']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict_yield', methods=['POST'])
def predict_yield():
    if not MODEL_TRAINED: return jsonify({'error': 'Model nije treniran!'}), 400
    try:
        data = request.get_json()
        
        drought_index = data['average_rain_fall_mm_per_year'] / (data['avg_temp'] + 20)
        
        input_data = data.copy()
        input_data['drought_index'] = drought_index
        
        input_df = pd.DataFrame({col: [input_data[col]] for col in FEATURE_ORDER})
        prediction = MODEL_PIPELINE.predict(input_df)
        predicted_yield = round(prediction[0] / 10, 2)

        history_years, history_yields = [], []
        if DF_META is not None and not DF_META.empty:
            history = DF_META[(DF_META['Area'] == data['Area']) & (DF_META['Item'] == data['Item'])].sort_values(by='Year').tail(10)
            history_years = history['Year'].tolist()
            history_yields = [round(y/10, 2) for y in history['hg/ha_yield'].tolist()]
            
        if not history_years:
             history_years = [data['Year']]
             history_yields = [predicted_yield]

        return jsonify({
            'status': 'success',
            'predicted_yield_kg_ha': predicted_yield,
            'history_years': history_years,
            'history_yields': history_yields,
            'prediction_year': data['Year']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=False, use_reloader=False)