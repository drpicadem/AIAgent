const API_URL = 'http://127.0.0.1:5000';
let myChart = null;
let countryStatsData = {};
let lastPredictionData = null;
const ENABLE_AUTO_SAVE = true;

function showToast(message, type = 'info', title = '') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    const titles = { success: title || 'Uspješno!', error: title || 'Greška!', warning: title || 'Upozorenje!', info: title || 'Informacija' };

    toast.innerHTML = `
        <i class="fas ${icons[type]} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${titles[type]}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>
    `;
    container.appendChild(toast);
    setTimeout(() => { toast.classList.add('hiding'); setTimeout(() => toast.remove(), 300); }, 3000);
}

const countryData = {
    "Afghanistan": { code: "af", name: "Afganistan" }, "Albania": { code: "al", name: "Albanija" }, "Algeria": { code: "dz", name: "Alžir" }, "Angola": { code: "ao", name: "Angola" }, "Argentina": { code: "ar", name: "Argentina" }, "Armenia": { code: "am", name: "Armenija" }, "Australia": { code: "au", name: "Australija" }, "Austria": { code: "at", name: "Austrija" }, "Azerbaijan": { code: "az", name: "Azerbejdžan" }, "Bahamas": { code: "bs", name: "Bahami" }, "Bahrain": { code: "bh", name: "Bahrein" }, "Bangladesh": { code: "bd", name: "Bangladeš" }, "Belarus": { code: "by", name: "Bjelorusija" }, "Belgium": { code: "be", name: "Belgija" }, "Botswana": { code: "bw", name: "Bocvana" }, "Brazil": { code: "br", name: "Brazil" }, "Bulgaria": { code: "bg", name: "Bugarska" }, "Burkina Faso": { code: "bf", name: "Burkina Faso" }, "Burundi": { code: "bi", name: "Burundi" }, "Cameroon": { code: "cm", name: "Kamerun" }, "Canada": { code: "ca", name: "Kanada" }, "Central African Republic": { code: "cf", name: "Srednjoafrička Republika" }, "Chile": { code: "cl", name: "Čile" }, "China": { code: "cn", name: "Kina" }, "Colombia": { code: "co", name: "Kolumbija" }, "Congo": { code: "cg", name: "Kongo" }, "Costa Rica": { code: "cr", name: "Kostarika" }, "Croatia": { code: "hr", name: "Hrvatska" }, "Cuba": { code: "cu", name: "Kuba" }, "Cyprus": { code: "cy", name: "Cipar" }, "Czech Republic": { code: "cz", name: "Češka" }, "Democratic Republic of the Congo": { code: "cd", name: "DR Kongo" }, "Denmark": { code: "dk", name: "Danska" }, "Dominican Republic": { code: "do", name: "Dominikanska Republika" }, "Ecuador": { code: "ec", name: "Ekvador" }, "Egypt": { code: "eg", name: "Egipat" }, "El Salvador": { code: "sv", name: "Salvador" }, "Eritrea": { code: "er", name: "Eritreja" }, "Estonia": { code: "ee", name: "Estonija" }, "Ethiopia": { code: "et", name: "Etiopija" }, "Finland": { code: "fi", name: "Finska" }, "France": { code: "fr", name: "Francuska" }, "Germany": { code: "de", name: "Njemačka" }, "Ghana": { code: "gh", name: "Gana" }, "Greece": { code: "gr", name: "Grčka" }, "Guatemala": { code: "gt", name: "Gvatemala" }, "Guinea": { code: "gn", name: "Gvineja" }, "Guyana": { code: "gy", name: "Gvajana" }, "Haiti": { code: "ht", name: "Haiti" }, "Honduras": { code: "hn", name: "Honduras" }, "Hungary": { code: "hu", name: "Mađarska" }, "India": { code: "in", name: "Indija" }, "Indonesia": { code: "id", name: "Indonezija" }, "Iraq": { code: "iq", name: "Irak" }, "Ireland": { code: "ie", name: "Irska" }, "Italy": { code: "it", name: "Italija" }, "Jamaica": { code: "jm", name: "Jamajka" }, "Japan": { code: "jp", name: "Japan" }, "Kazakhstan": { code: "kz", name: "Kazahstan" }, "Kenya": { code: "ke", name: "Kenija" }, "Latvia": { code: "lv", name: "Latvija" }, "Lebanon": { code: "lb", name: "Libanon" }, "Lesotho": { code: "ls", name: "Lesoto" }, "Liberia": { code: "lr", name: "Liberija" }, "Libya": { code: "ly", name: "Libija" }, "Lithuania": { code: "lt", name: "Litva" }, "Madagascar": { code: "mg", name: "Madagaskar" }, "Malawi": { code: "mw", name: "Malavi" }, "Malaysia": { code: "my", name: "Malezija" }, "Mali": { code: "ml", name: "Mali" }, "Malta": { code: "mt", name: "Malta" }, "Mauritania": { code: "mr", name: "Mauritanija" }, "Mauritius": { code: "mu", name: "Mauricijus" }, "Mexico": { code: "mx", name: "Meksiko" }, "Montenegro": { code: "me", name: "Crna Gora" }, "Morocco": { code: "ma", name: "Maroko" }, "Mozambique": { code: "mz", name: "Mozambik" }, "Myanmar": { code: "mm", name: "Mjanmar" }, "Namibia": { code: "na", name: "Namibija" }, "Nepal": { code: "np", name: "Nepal" }, "Netherlands": { code: "nl", name: "Nizozemska" }, "New Zealand": { code: "nz", name: "Novi Zeland" }, "Nicaragua": { code: "ni", name: "Nikaragva" }, "Niger": { code: "ne", name: "Niger" }, "Nigeria": { code: "ng", name: "Nigerija" }, "North Korea": { code: "kp", name: "Sjeverna Koreja" }, "Norway": { code: "no", name: "Norveška" }, "Pakistan": { code: "pk", name: "Pakistan" }, "Papua New Guinea": { code: "pg", name: "Papua Nova Gvineja" }, "Paraguay": { code: "py", name: "Paragvaj" }, "Peru": { code: "pe", name: "Peru" }, "Philippines": { code: "ph", name: "Filipini" }, "Poland": { code: "pl", name: "Poljska" }, "Portugal": { code: "pt", name: "Portugal" }, "Qatar": { code: "qa", name: "Katar" }, "Romania": { code: "ro", name: "Rumunija" }, "Russia": { code: "ru", name: "Rusija" }, "Rwanda": { code: "rw", name: "Ruanda" }, "Saudi Arabia": { code: "sa", name: "Saudijska Arabija" }, "Senegal": { code: "sn", name: "Senegal" }, "Serbia": { code: "rs", name: "Srbija" }, "Sierra Leone": { code: "sl", name: "Sijera Leone" }, "Slovakia": { code: "sk", name: "Slovačka" }, "Slovenia": { code: "si", name: "Slovenija" }, "South Africa": { code: "za", name: "Južna Afrika" }, "South Korea": { code: "kr", name: "Južna Koreja" }, "Spain": { code: "es", name: "Španija" }, "Sri Lanka": { code: "lk", name: "Šri Lanka" }, "Sudan": { code: "sd", name: "Sudan" }, "Suriname": { code: "sr", name: "Surinam" }, "Sweden": { code: "se", name: "Švedska" }, "Switzerland": { code: "ch", name: "Švicarska" }, "Tajikistan": { code: "tj", name: "Tadžikistan" }, "Tanzania": { code: "tz", name: "Tanzanija" }, "Thailand": { code: "th", name: "Tajland" }, "Tunisia": { code: "tn", name: "Tunis" }, "Turkey": { code: "tr", name: "Turska" }, "Uganda": { code: "ug", name: "Uganda" }, "Ukraine": { code: "ua", name: "Ukrajina" }, "United Arab Emirates": { code: "ae", name: "UAE" }, "United Kingdom": { code: "gb", name: "Ujedinjeno Kraljevstvo" }, "United States": { code: "us", name: "SAD" }, "Uruguay": { code: "uy", name: "Urugvaj" }, "Uzbekistan": { code: "uz", name: "Uzbekistan" }, "Venezuela": { code: "ve", name: "Venecuela" }, "Vietnam": { code: "vn", name: "Vijetnam" }, "Yemen": { code: "ye", name: "Jemen" }, "Zambia": { code: "zm", "name": "Zambija" }, "Zimbabwe": { code: "zw", name: "Zimbabve" }
};

const cropData = {
    "Maize": { icon: "🌽", name: "Kukuruz" }, "Potatoes": { icon: "🥔", name: "Krompir" }, "Rice, paddy": { icon: "🍚", name: "Riža" }, "Wheat": { icon: "🌾", name: "Pšenica" }, "Soybeans": { icon: "🌱", name: "Soja" }, "Sorghum": { icon: "🥣", name: "Sirak" }, "Barley": { icon: "🍺", name: "Ječam" }, "Cassava": { icon: "🍠", name: "Manioka" }, "Yams": { icon: "🍠", name: "Jam" }, "Sweet potatoes": { icon: "🍠", name: "Batat" }, "Plantains and others": { icon: "🍌", name: "Trputac" }
};

function formatCountry(state) {
    if (!state.id) return state.text;
    const info = countryData[state.id.trim()] || { code: "globe", name: state.id };
    const img = info.code === "globe" ? "" : `<img src="https://flagcdn.com/w40/${info.code}.png" class="flag-icon" />`;
    return $(`<span>${img} ${info.name}</span>`);
}

function formatCrop(state) {
    if (!state.id) return state.text;
    const info = cropData[state.id.trim()] || { icon: "🌱", name: state.id };
    return $(`<span><span class="crop-icon">${info.icon}</span> ${info.name}</span>`);
}

$(document).ready(function () {
    $('#Area').select2({ placeholder: "Odaberite državu...", templateResult: formatCountry, templateSelection: formatCountry });
    $('#Item').select2({ placeholder: "Odaberite kulturu...", templateResult: formatCrop, templateSelection: formatCrop });

    loadMetadata();
    checkModelStatus();
});

async function checkModelStatus() {
    try {
        const response = await fetch(`${API_URL}/model_status`);
        const data = await response.json();
        updateModelStatusUI(data.model_trained);
    } catch (error) {
        console.error('Greška pri provjeri statusa modela:', error);
        updateModelStatusUI(false);
    }
}

function updateModelStatusUI(isTrained) {
    const statusEl = $('#modelStatus');
    const submitBtn = $('#submitBtn');
    if (isTrained) {
        statusEl.html('<i class="fas fa-check-circle"></i> Model Treniran');
        submitBtn.prop('disabled', false);
    } else {
        statusEl.html('<i class="fas fa-times-circle"></i> Model Nije Treniran');
        submitBtn.prop('disabled', true);
    }
}

$('#btnTrainModel').click(async function () {
    const btn = $(this);
    const originalContent = btn.html();
    if (!confirm('Treniranje modela može potrajati nekoliko minuta. Nastaviti?')) return;

    btn.html('<i class="fas fa-spinner fa-spin"></i> Treniram...');
    btn.prop('disabled', true);

    try {
        const response = await fetch(`${API_URL}/train_model`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        const data = await response.json();
        if (data.status === 'success') {
            showToast(`Model treniran!<br>R² score: ${data.r2_score}`, 'success', 'Uspjeh!');
            updateModelStatusUI(true);
        } else {
            showToast(data.error || 'Greška pri treniranju', 'error');
        }
    } catch (error) {
        showToast('Nije moguće trenirati model.', 'error');
    } finally {
        btn.html(originalContent);
        btn.prop('disabled', false);
    }
});

async function autoSaveData(predictionData) {
    if (!predictionData || !ENABLE_AUTO_SAVE) return;

    try {
        const response = await fetch(`${API_URL}/save_data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(predictionData)
        });

        const data = await response.json();

        if (data.status === 'success') {

        } else {
            console.error('❌ Greška pri spremanju:', data.error);
        }
    } catch (error) {
        console.error('❌ Mrežna greška pri spremanju podataka:', error);
    }
}

$('#btnLiveWeather').click(async function () {
    const country = $('#Area').val();
    if (!country) { showToast('Molim odaberite državu prvo!', 'warning'); return; }

    const btn = $(this);
    const originalContent = btn.html();
    btn.html('<i class="fas fa-spinner fa-spin"></i>');
    btn.prop('disabled', true);

    try {
        const response = await fetch(`${API_URL}/get_live_weather`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ country: country })
        });
        const data = await response.json();

        if (data.status === 'success') {
            $('#avg_temp').val(data.temp).addClass('live-update');
            setTimeout(() => $('#avg_temp').removeClass('live-update'), 1000);
            showToast(`Lokacija: ${data.note}<br>Temp: ${data.temp}°C`, 'success');
        } else {
            showToast(data.error || 'Greška', 'error');
        }
    } catch (e) {
        showToast('Greška s live podacima.', 'error');
    } finally {
        btn.html(originalContent);
        btn.prop('disabled', false);
    }
});

$('#Area').on('select2:select', function (e) {
    const country = e.params.data.id.trim();
    if (countryStatsData[country]) {
        const stats = countryStatsData[country];
        $('#average_rain_fall_mm_per_year').val(Math.round(stats.average_rain_fall_mm_per_year || 0));
        $('#avg_temp').val((stats.avg_temp || 0).toFixed(1));
        $('#pesticides_tonnes').val((stats.pesticides_tonnes || 0).toFixed(1));
    }
});

async function loadMetadata() {
    try {
        const response = await fetch(`${API_URL}/get_metadata`);
        const data = await response.json();
        if (data.status === 'success') {
            countryStatsData = data.country_stats;
            updateModelStatusUI(data.model_trained);
            data.areas.forEach(area => $('#Area').append(new Option(area, area)));
            data.items.forEach(item => $('#Item').append(new Option(item, item)));
        }
    } catch (error) { console.error('Error loading metadata', error); }
}

$('#predictionForm').on('submit', async function (e) {
    e.preventDefault();

    const $submitBtn = $('#submitBtn');
    const originalBtnHtml = $submitBtn.html();

    $submitBtn.prop('disabled', true);
    $submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Izračunavam...');
    $('#errorMessage').hide();
    $('#result-section').slideUp();

    const formData = {
        Area: $('#Area').val(),
        Item: $('#Item').val(),
        Year: parseInt($('#Year').val()),
        average_rain_fall_mm_per_year: parseFloat($('#average_rain_fall_mm_per_year').val()),
        pesticides_tonnes: parseFloat($('#pesticides_tonnes').val()),
        avg_temp: parseFloat($('#avg_temp').val())
    };

    try {
        const response = await fetch(`${API_URL}/predict_yield`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.status === 'success') {
            lastPredictionData = {
                Area: formData.Area,
                Item: formData.Item,
                Year: formData.Year,
                predicted_yield: data.predicted_yield_kg_ha,
                average_rain_fall_mm_per_year: formData.average_rain_fall_mm_per_year,
                pesticides_tonnes: formData.pesticides_tonnes,
                avg_temp: formData.avg_temp
            };

            $('#yieldResult').text(data.predicted_yield_kg_ha.toLocaleString());
            $('#dunumResult').text((data.predicted_yield_kg_ha / 10000).toFixed(2));
            $('#result-section').slideDown();

            const ctx = document.getElementById('yieldChart').getContext('2d');
            if (myChart) myChart.destroy();

            const lastHistoryValue = data.history_yields[data.history_yields.length - 1];
            const predictionDataset = [...Array(data.history_years.length - 1).fill(null), lastHistoryValue, data.predicted_yield_kg_ha];

            myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [...data.history_years, data.prediction_year],
                    datasets: [{
                        label: 'Historijski prinos',
                        data: data.history_yields,
                        borderColor: '#11998e',
                        backgroundColor: 'rgba(17, 153, 142, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Predviđeni prinos',
                        data: predictionDataset,
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.2)',
                        pointRadius: 8,
                        spanGaps: true
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });

            if (ENABLE_AUTO_SAVE) {
                setTimeout(() => {
                    autoSaveData(lastPredictionData);
                }, 500);
            }

        } else if (data.status === 'no_data') {
            showToast(data.message, 'warning');
            $('#result-section').slideUp();
        } else {
            $('#errorMessage').text(data.error || 'Greška').show();
        }
    } catch (error) {
        $('#errorMessage').text('Greška servera: ' + error.message).show();
    } finally {
        $submitBtn.prop('disabled', false);
        $submitBtn.html(originalBtnHtml);
    }
});
