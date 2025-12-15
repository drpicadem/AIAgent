# Agri-AI Commerce 🚜

Sistem za pametno predviđanje prinosa u poljoprivredi korištenjem mašinskog učenja.

## 🌟 Mogućnosti (Features)

*   **Predviđanje Prinosa**: Napredna predikcija prinosa (hg/ha) na osnovu historijskih podataka i faktora okoliša.
*   **Live Vremenski Podaci**: Dohvaćanje trenutne temperature za odabranu lokaciju u stvarnom vremenu.
*   **Interaktivni Grafovi**: Vizualizacija historijskih i predviđenih podataka o prinosu.
*   **Treniranje Modela**: Mogućnost treniranja/retreniranja Random Forest modela direktno iz korisničkog interfejsa.
*   **Automatsko Spremanje**: Novi podaci predikcija se automatski spremaju u dataset za buduće treniranje.
*   **Moderni Dizajn**: Responsive UI sa animacijama, prilagođen za sve uređaje.

## 🛠️ Tehnologije

*   **Backend**: Python, Flask
*   **Frontend**: HTML5, CSS3, JavaScript (jQuery, Chart.js, Select2)
*   **Machine Learning**: Scikit-Learn, Pandas, NumPy, Joblib

## 🚀 Instalacija

1.  Klonirajte repozitorij:
    ```bash
    git clone https://github.com/drpicadem/AIAgent.git
    cd AIAgent
    ```

2.  Kreirajte i aktivirajte virtualno okruženje (preporučeno):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  Instalirajte potrebne biblioteke:
    ```bash
    pip install flask flask-cors pandas numpy scikit-learn joblib requests
    ```

4.  (Opcionalno) Ručno treniranje modela:
    ```bash
    python train_model.py
    ```

## 🏃 Pokretanje

1.  Pokrenite Flask aplikaciju:
    ```bash
    python app.py
    ```

2.  Otvorite browser i idite na:
    `http://127.0.0.1:5000`


