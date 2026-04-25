import streamlit as st
import numpy as np
from PIL import Image
import io

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LeafScan AI – Plant Disease Detector",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --green-deep: #1a3a2a;
  --green-mid:  #2d6a4f;
  --green-light:#52b788;
  --green-pale: #d8f3dc;
  --accent:     #f4a261;
  --cream:      #faf7f2;
  --text-dark:  #1a2e1e;
  --text-mid:   #4a6741;
  --radius:     16px;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--cream);
  font-family: 'DM Sans', sans-serif;
  color: var(--text-dark);
}

[data-testid="stHeader"] { background: transparent; }

/* ── Hero ── */
.hero {
  text-align: center;
  padding: 3rem 1rem 1.5rem;
}
.hero h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.2rem, 5vw, 3.8rem);
  font-weight: 900;
  color: var(--green-deep);
  line-height: 1.1;
  margin: 0;
}
.hero h1 span { color: var(--green-light); }
.hero p {
  margin: .8rem auto 0;
  max-width: 520px;
  font-size: 1.05rem;
  color: var(--text-mid);
  font-weight: 300;
}

/* ── Upload zone ── */
.upload-zone {
  background: white;
  border: 2.5px dashed var(--green-light);
  border-radius: var(--radius);
  padding: 2.5rem;
  text-align: center;
  transition: border-color .2s;
  margin-bottom: 1.5rem;
}
.upload-zone:hover { border-color: var(--green-mid); }

/* ── Cards ── */
.result-card {
  background: white;
  border-radius: var(--radius);
  padding: 1.6rem 1.8rem;
  margin-bottom: 1.2rem;
  box-shadow: 0 2px 16px rgba(45,106,79,.08);
  border-left: 5px solid var(--green-light);
}
.result-card.warning { border-left-color: #e76f51; }
.result-card.healthy { border-left-color: #52b788; }

.disease-name {
  font-family: 'Playfair Display', serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--green-deep);
  margin: 0 0 .2rem;
}
.confidence-badge {
  display: inline-block;
  background: var(--green-pale);
  color: var(--green-mid);
  font-weight: 600;
  font-size: .85rem;
  padding: .25rem .75rem;
  border-radius: 999px;
  margin-bottom: 1rem;
}
.confidence-badge.high   { background:#d8f3dc; color:#1b4332; }
.confidence-badge.medium { background:#fff3cd; color:#856404; }
.confidence-badge.low    { background:#f8d7da; color:#721c24; }

.section-label {
  font-size: .75rem;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--text-mid);
  margin: 1rem 0 .4rem;
}
.info-text {
  font-size: .95rem;
  line-height: 1.65;
  color: #3a5240;
}
.pill-list { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .4rem; }
.pill {
  background: var(--green-pale);
  color: var(--green-mid);
  border-radius: 999px;
  padding: .3rem .9rem;
  font-size: .85rem;
  font-weight: 500;
}

/* ── Progress bar ── */
.conf-bar-wrap { height: 8px; background: #e8f5e9; border-radius: 999px; overflow: hidden; margin-top: .3rem; }
.conf-bar      { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--green-light), var(--green-mid)); transition: width .6s ease; }

/* ── Footer ── */
.footer {
  text-align: center;
  padding: 2rem 0 1rem;
  font-size: .8rem;
  color: var(--text-mid);
  opacity: .7;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer { visibility: hidden; }
.stFileUploader label { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Disease database ───────────────────────────────────────────────────────────
DISEASE_DB = {
    # Apple
    "Apple___Apple_scab": {
        "display": "Apple – Apple Scab",
        "healthy": False,
        "cause": "Fungal infection caused by *Venturia inaequalis*. Spreads via spores in wet, cool spring weather.",
        "symptoms": "Olive-green to brown velvety spots on leaves; fruit lesions that crack and deform.",
        "cure": "Apply fungicides (myclobutanil, captan) at bud-break. Remove and destroy fallen leaves. Prune for air circulation.",
        "prevention": ["Plant scab-resistant varieties", "Rake fallen leaves in autumn", "Avoid overhead irrigation", "Apply dormant copper sprays"],
    },
    "Apple___Black_rot": {
        "display": "Apple – Black Rot",
        "healthy": False,
        "cause": "Fungus *Botryosphaeria obtusa*. Infects through wounds; spores spread by rain.",
        "symptoms": "Purple-bordered leaf spots, rotting fruit with concentric rings, cankers on branches.",
        "cure": "Prune out infected branches 8–12 inches below cankers. Apply captan or thiophanate-methyl fungicides.",
        "prevention": ["Remove mummified fruit", "Prune dead wood", "Maintain tree vigor", "Avoid wounding bark"],
    },
    "Apple___Cedar_apple_rust": {
        "display": "Apple – Cedar Apple Rust",
        "healthy": False,
        "cause": "Fungus *Gymnosporangium juniperi-virginianae* that alternates between apple and juniper/cedar trees.",
        "symptoms": "Bright orange-yellow spots on upper leaf surface; tubular spore structures beneath.",
        "cure": "Apply myclobutanil or mancozeb at petal-fall and repeat every 7–10 days. Remove nearby juniper galls.",
        "prevention": ["Plant resistant varieties", "Remove cedar/juniper hosts within 1 km", "Apply preventive fungicide in spring"],
    },
    "Apple___healthy": {"display": "Apple – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Maintain regular pruning", "Monitor for early symptoms"]},
    # Blueberry
    "Blueberry___healthy": {"display": "Blueberry – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Mulch around plants", "Test soil pH annually"]},
    # Cherry
    "Cherry_(including_sour)___Powdery_mildew": {
        "display": "Cherry – Powdery Mildew",
        "healthy": False,
        "cause": "Fungus *Podosphaera clandestina*; thrives in warm days and cool nights with high humidity.",
        "symptoms": "White powdery coating on young leaves and shoots; leaves curl and distort.",
        "cure": "Spray sulfur, potassium bicarbonate, or myclobutanil. Remove heavily infected shoots.",
        "prevention": ["Improve air circulation by pruning", "Avoid excess nitrogen fertilizer", "Water at base not overhead"],
    },
    "Cherry_(including_sour)___healthy": {"display": "Cherry – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Annual pruning", "Balanced fertilization"]},
    # Corn
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "display": "Corn – Gray Leaf Spot",
        "healthy": False,
        "cause": "Fungus *Cercospora zeae-maydis*; favored by warm, humid conditions and crop residue.",
        "symptoms": "Rectangular gray-tan lesions between leaf veins; severe cases cause premature leaf death.",
        "cure": "Apply strobilurin or triazole fungicides at tasseling. Till under crop residue.",
        "prevention": ["Rotate crops", "Plant resistant hybrids", "Improve field drainage", "Avoid dense planting"],
    },
    "Corn_(maize)___Common_rust_": {
        "display": "Corn – Common Rust",
        "healthy": False,
        "cause": "Fungus *Puccinia sorghi*; spores blown in from southern regions each year.",
        "symptoms": "Brick-red oval pustules on both leaf surfaces that release powdery spores.",
        "cure": "Apply propiconazole or azoxystrobin at first sign. Resistant hybrids are the best long-term solution.",
        "prevention": ["Plant rust-resistant hybrids", "Early planting to avoid peak spore season", "Monitor weekly during season"],
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "display": "Corn – Northern Leaf Blight",
        "healthy": False,
        "cause": "Fungus *Setosphaeria turcica*; spreads in moderate temperatures with extended leaf wetness.",
        "symptoms": "Large cigar-shaped tan lesions (up to 15 cm) on leaves; dark sporulation in humid conditions.",
        "cure": "Fungicide application (azoxystrobin) at VT/R1 stage. Bury infected residue by tillage.",
        "prevention": ["Use resistant hybrids", "Rotate with non-host crops", "Reduce crop residue on surface"],
    },
    "Corn_(maize)___healthy": {"display": "Corn – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Crop rotation", "Balanced NPK fertilization"]},
    # Grape
    "Grape___Black_rot": {
        "display": "Grape – Black Rot",
        "healthy": False,
        "cause": "Fungus *Guignardia bidwellii*; overwinterns in mummified fruit and infected canes.",
        "symptoms": "Brown leaf spots with dark borders; fruit shrivels into hard black mummies.",
        "cure": "Apply myclobutanil or mancozeb from bud-break through bunch closure. Remove mummified fruit.",
        "prevention": ["Remove mummies and infected canes during pruning", "Open canopy for airflow", "Apply preventive fungicide schedule"],
    },
    "Grape___Esca_(Black_Measles)": {
        "display": "Grape – Esca (Black Measles)",
        "healthy": False,
        "cause": "Wood-rotting fungi (*Phaeomoniella*, *Phaeoacremonium*); enters through pruning wounds.",
        "symptoms": "Tiger-stripe leaf discoloration; berry shriveling; internal wood decay.",
        "cure": "No complete cure. Remove and burn infected wood. Protect pruning wounds with fungicidal paste.",
        "prevention": ["Prune in dry weather", "Seal cuts with wound protectant", "Avoid large pruning wounds"],
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "display": "Grape – Leaf Blight",
        "healthy": False,
        "cause": "Fungus *Pseudocercospora vitis*; favored by warm, humid conditions.",
        "symptoms": "Angular dark spots on older leaves; premature defoliation.",
        "cure": "Apply copper-based or mancozeb fungicides. Remove infected leaves.",
        "prevention": ["Maintain vine canopy openness", "Avoid wetting foliage", "End-of-season sanitation"],
    },
    "Grape___healthy": {"display": "Grape – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Regular canopy management", "Balanced irrigation"]},
    # Orange
    "Orange___Haunglongbing_(Citrus_greening)": {
        "display": "Orange – Huanglongbing (Citrus Greening)",
        "healthy": False,
        "cause": "Bacteria *Candidatus Liberibacter asiaticus* spread by Asian citrus psyllid insects.",
        "symptoms": "Asymmetric 'blotchy mottle' yellowing of leaves; small misshapen bitter fruit; twig dieback.",
        "cure": "No cure exists. Remove and destroy infected trees promptly to protect neighbors. Control psyllid with imidacloprid.",
        "prevention": ["Use certified disease-free nursery stock", "Control psyllid populations", "Quarantine new plants", "Regular scouting"],
    },
    # Peach
    "Peach___Bacterial_spot": {
        "display": "Peach – Bacterial Spot",
        "healthy": False,
        "cause": "Bacterium *Xanthomonas arboricola* pv. *pruni*; spreads in wet, windy conditions.",
        "symptoms": "Water-soaked leaf spots turning purple-brown with yellow halos; fruit cracking.",
        "cure": "Apply copper bactericides preventively. Avoid overhead irrigation. Prune for air flow.",
        "prevention": ["Plant resistant varieties", "Use windbreaks", "Avoid wounding fruit", "Apply copper at petal fall"],
    },
    "Peach___healthy": {"display": "Peach – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Annual pruning", "Thin fruit for size"]},
    # Pepper
    "Pepper,_bell___Bacterial_spot": {
        "display": "Bell Pepper – Bacterial Spot",
        "healthy": False,
        "cause": "Bacterium *Xanthomonas campestris* pv. *vesicatoria*; seed-borne and spread by rain splash.",
        "symptoms": "Small water-soaked spots turning brown with yellow halos on leaves; scabby fruit lesions.",
        "cure": "Apply copper + mancozeb sprays. Use disease-free seed. Remove infected plants.",
        "prevention": ["Use certified disease-free seeds", "Crop rotation (3 years)", "Drip irrigation", "Avoid working in wet fields"],
    },
    "Pepper,_bell___healthy": {"display": "Bell Pepper – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Proper spacing", "Drip irrigation preferred"]},
    # Potato
    "Potato___Early_blight": {
        "display": "Potato – Early Blight",
        "healthy": False,
        "cause": "Fungus *Alternaria solani*; overwinters in soil and plant debris.",
        "symptoms": "Dark brown lesions with concentric rings (target board pattern) on older leaves.",
        "cure": "Apply chlorothalonil, mancozeb, or azoxystrobin. Remove infected lower leaves.",
        "prevention": ["Crop rotation (3 years)", "Plant certified seed tubers", "Avoid stress from drought or nutrient deficiency", "Mulch to reduce soil splash"],
    },
    "Potato___Late_blight": {
        "display": "Potato – Late Blight",
        "healthy": False,
        "cause": "Oomycete *Phytophthora infestans*; caused the Irish Famine. Spreads rapidly in cool, wet weather.",
        "symptoms": "Water-soaked pale green spots that turn brown-black; white sporulation on undersides in humid conditions.",
        "cure": "Apply metalaxyl, cymoxanil, or chlorothalonil at first sign. Destroy infected foliage. Do not leave cull piles.",
        "prevention": ["Plant resistant varieties", "Use certified seed", "Hill soil to protect tubers", "Scout weekly during wet periods"],
    },
    "Potato___healthy": {"display": "Potato – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Certified seed tubers", "Proper hilling"]},
    # Raspberry
    "Raspberry___healthy": {"display": "Raspberry – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Annual cane removal post-harvest"]},
    # Soybean
    "Soybean___healthy": {"display": "Soybean – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Crop rotation", "Scout weekly"]},
    # Squash
    "Squash___Powdery_mildew": {
        "display": "Squash – Powdery Mildew",
        "healthy": False,
        "cause": "Fungi *Podosphaera xanthii* or *Erysiphe cichoracearum*; thrives in warm dry weather.",
        "symptoms": "White powdery coating on leaves and stems; leaves yellow and die prematurely.",
        "cure": "Spray potassium bicarbonate, neem oil, or sulfur fungicide. Remove heavily infected leaves.",
        "prevention": ["Plant resistant varieties", "Space plants for airflow", "Water in the morning"],
    },
    # Strawberry
    "Strawberry___Leaf_scorch": {
        "display": "Strawberry – Leaf Scorch",
        "healthy": False,
        "cause": "Fungus *Diplocarpon earlianum*; spores spread by rain splash in warm wet conditions.",
        "symptoms": "Small purple spots on upper leaf surface; spots enlarge, centers turn tan-gray; leaves look scorched.",
        "cure": "Apply myclobutanil or captan. Remove old infected foliage after harvest. Renovate beds.",
        "prevention": ["Plant resistant varieties", "Avoid overhead irrigation", "Good bed renovation after harvest", "Adequate spacing"],
    },
    "Strawberry___healthy": {"display": "Strawberry – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Renovation after harvest", "Proper fertilization"]},
    # Tomato
    "Tomato___Bacterial_spot": {
        "display": "Tomato – Bacterial Spot",
        "healthy": False,
        "cause": "Bacterium *Xanthomonas vesicatoria*; seed-borne, spread by rain and irrigation water.",
        "symptoms": "Small water-soaked spots on leaves; raised scabby lesions on fruit; defoliation.",
        "cure": "Copper + mancozeb sprays weekly. Use disease-free transplants. Avoid overhead watering.",
        "prevention": ["Disease-free certified seed", "3-year rotation", "Stake plants for airflow", "Drip irrigation"],
    },
    "Tomato___Early_blight": {
        "display": "Tomato – Early Blight",
        "healthy": False,
        "cause": "Fungus *Alternaria solani*; survives in soil and plant debris for years.",
        "symptoms": "Dark concentric ring lesions on older leaves; yellow halo around spots; stem collar rot possible.",
        "cure": "Chlorothalonil, mancozeb, or copper fungicides every 7–10 days. Prune lower infected leaves.",
        "prevention": ["Mulch to prevent soil splash", "Crop rotation", "Remove infected leaves promptly", "Adequate plant spacing"],
    },
    "Tomato___Late_blight": {
        "display": "Tomato – Late Blight",
        "healthy": False,
        "cause": "Oomycete *Phytophthora infestans*; same pathogen as potato late blight; spreads rapidly in cool wet conditions.",
        "symptoms": "Large greasy gray-green patches on leaves; white mold on undersides; brown fruit rot.",
        "cure": "Apply chlorothalonil, cymoxanil, or metalaxyl immediately. Remove infected plants to prevent spread.",
        "prevention": ["Plant resistant varieties", "Stake and prune for airflow", "Avoid wetting foliage", "Do not compost infected debris"],
    },
    "Tomato___Leaf_Mold": {
        "display": "Tomato – Leaf Mold",
        "healthy": False,
        "cause": "Fungus *Passalora fulva*; thrives in high humidity greenhouses and tunnels.",
        "symptoms": "Yellow spots on upper leaf surface; olive-brown fuzzy mold underneath.",
        "cure": "Increase ventilation. Apply copper or chlorothalonil. Remove infected leaves.",
        "prevention": ["Reduce humidity below 85%", "Improve airflow", "Plant resistant varieties", "Avoid leaf wetness"],
    },
    "Tomato___Septoria_leaf_spot": {
        "display": "Tomato – Septoria Leaf Spot",
        "healthy": False,
        "cause": "Fungus *Septoria lycopersici*; overwinters on plant debris; spreads by rain.",
        "symptoms": "Numerous small circular spots with dark borders and light centers; spots appear on older leaves first.",
        "cure": "Chlorothalonil or mancozeb every 7–10 days. Remove infected foliage. Mulch soil.",
        "prevention": ["Crop rotation", "Stake plants", "Mulch around base", "Remove lower leaves proactively"],
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "display": "Tomato – Spider Mites",
        "healthy": False,
        "cause": "Two-spotted spider mite (*Tetranychus urticae*); thrives in hot, dry conditions. Not a fungus — an arachnid pest.",
        "symptoms": "Stippled, bronze/yellowing leaves; fine webbing on underside; leaves dry up and drop.",
        "cure": "Spray insecticidal soap, neem oil, or abamectin. Release predatory mites (*Phytoseiulus persimilis*). Increase humidity.",
        "prevention": ["Avoid water stress", "Inspect undersides of leaves regularly", "Avoid dusty conditions", "Avoid broad-spectrum insecticides that kill predators"],
    },
    "Tomato___Target_Spot": {
        "display": "Tomato – Target Spot",
        "healthy": False,
        "cause": "Fungus *Corynespora cassiicola*; favored by warm temperatures and prolonged leaf wetness.",
        "symptoms": "Concentric ring lesions on leaves, stems, and fruit; defoliation from the bottom up.",
        "cure": "Apply azoxystrobin or chlorothalonil. Prune for airflow. Destroy infected debris.",
        "prevention": ["Crop rotation", "Staking for good air circulation", "Drip irrigation", "Avoid overhead watering"],
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "display": "Tomato – Yellow Leaf Curl Virus",
        "healthy": False,
        "cause": "Begomovirus transmitted by whitefly (*Bemisia tabaci*); spreads rapidly in warm climates.",
        "symptoms": "Severe stunting; leaves cup upward and turn yellow at edges; flower drop; little or no fruit.",
        "cure": "No cure once infected. Remove and destroy infected plants. Control whitefly with imidacloprid or insecticidal soap.",
        "prevention": ["Use virus-resistant varieties", "Install reflective mulch", "Yellow sticky traps for whitefly monitoring", "Avoid planting near infected crops"],
    },
    "Tomato___Tomato_mosaic_virus": {
        "display": "Tomato – Mosaic Virus",
        "healthy": False,
        "cause": "Tobamovirus transmitted by contact, tools, and hands. Extremely stable — survives in dried plant debris for years.",
        "symptoms": "Mosaic light/dark green leaf mottling; leaf distortion; stunted growth; poor fruit set.",
        "cure": "No cure. Remove and destroy infected plants. Sanitize tools with 10% bleach solution.",
        "prevention": ["Use certified virus-free seed", "Wash hands before working with plants", "Disinfect tools frequently", "Do not smoke near plants (tobacco carries TMV)"],
    },
    "Tomato___healthy": {"display": "Tomato – Healthy", "healthy": True, "cause": "", "symptoms": "", "cure": "No treatment needed.", "prevention": ["Regular inspection", "Balanced fertilization", "Proper watering"]},
}

CLASS_NAMES = list(DISEASE_DB.keys())

# ── Model loading ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model():
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model("plant_disease_mobilenetv2.keras")
        return model, "keras"
    except Exception:
        pass
    try:
        try:
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            import tensorflow as tf
            Interpreter = tf.lite.Interpreter
        interpreter = Interpreter(model_path="model.tflite")
        interpreter.allocate_tensors()
        return interpreter, "tflite"
    except Exception:
        pass
    return None, None

def predict(model, model_type, img: Image.Image):
    import tensorflow as tf
    img = img.convert("RGB").resize((128, 128))
    arr = np.array(img, dtype=np.float32)
    arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)
    arr = np.expand_dims(arr, 0)

    if model_type == "keras":
        preds = model.predict(arr, verbose=0)[0]
    else:
        inp = model.get_input_details()[0]
        out = model.get_output_details()[0]
        model.set_tensor(inp['index'], arr)
        model.invoke()
        preds = model.get_tensor(out['index'])[0]

    top3_idx = np.argsort(preds)[::-1][:3]
    results = []
    for i in top3_idx:
        if i < len(CLASS_NAMES):
            results.append({
                "label": CLASS_NAMES[i],
                "confidence": float(preds[i]) * 100,
                "info": DISEASE_DB.get(CLASS_NAMES[i], {}),
            })
    return results

def confidence_class(conf):
    if conf >= 75: return "high"
    if conf >= 45: return "medium"
    return "low"

# ── UI ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🌿 Leaf<span>Scan</span> AI</h1>
  <p>Upload any plant leaf image — instantly detect diseases, understand causes, and get cure & prevention advice.</p>
</div>
""", unsafe_allow_html=True)

# Load model
model, model_type = load_model()
if model is None:
    st.error("⚠️ No model file found. Please upload `plant_disease_mobilenetv2.keras` or `model.tflite` to the app directory.")

# ── Upload ──
col_upload, col_result = st.columns([1, 1.3], gap="large")

with col_upload:
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drop a leaf image here",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        label_visibility="visible"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Uploaded leaf", use_container_width=True)

with col_result:
    if uploaded and model:
        with st.spinner("🔍 Analysing leaf..."):
            results = predict(model, model_type, img)

        top = results[0]
        info = top["info"]
        conf = top["confidence"]
        cc   = confidence_class(conf)
        healthy = info.get("healthy", False)

        card_class = "healthy" if healthy else "warning"
        st.markdown(f"""
        <div class="result-card {card_class}">
          <div class="disease-name">{"✅ " if healthy else "⚠️ "}{info.get("display", top["label"])}</div>
          <div class="confidence-badge {cc}">Confidence: {conf:.1f}%</div>
          <div class="conf-bar-wrap"><div class="conf-bar" style="width:{conf:.1f}%"></div></div>
        """, unsafe_allow_html=True)

        if not healthy:
            st.markdown(f"""
          <div class="section-label">Cause</div>
          <div class="info-text">{info.get("cause","")}</div>
          <div class="section-label">Symptoms</div>
          <div class="info-text">{info.get("symptoms","")}</div>
          <div class="section-label">Treatment / Cure</div>
          <div class="info-text">{info.get("cure","")}</div>
          <div class="section-label">Prevention Tips</div>
          <div class="pill-list">
            {"".join(f'<span class="pill">🛡 {p}</span>' for p in info.get("prevention",[]))}
          </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
          <div class="info-text" style="margin-top:.5rem">Your plant looks healthy! Keep up the good care.</div>
          <div class="section-label">Ongoing Care Tips</div>
          <div class="pill-list">
            {"".join(f'<span class="pill">✓ {p}</span>' for p in info.get("prevention",[]))}
          </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Top 3
        if len(results) > 1:
            st.markdown('<div class="section-label" style="margin-top:1rem">Other Possibilities</div>', unsafe_allow_html=True)
            for r in results[1:]:
                c2 = confidence_class(r["confidence"])
                lbl = r["info"].get("display", r["label"])
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.5rem;">
                  <span style="font-size:.9rem;flex:1;color:#3a5240;">{lbl}</span>
                  <span class="confidence-badge {c2}">{r["confidence"]:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)

    elif uploaded and model is None:
        st.info("Model not loaded. See error above.")
    else:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:300px;color:#6a9070;text-align:center;gap:1rem;">
          <div style="font-size:3.5rem;">🌱</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:#2d6a4f;">Upload a leaf to begin</div>
          <div style="font-size:.9rem;max-width:260px;line-height:1.5;">Supports any plant species — tomato, potato, apple, grape, corn and many more.</div>
        </div>
        """, unsafe_allow_html=True)

# ── Supported plants ──
st.divider()
st.markdown('<div class="section-label" style="text-align:center;font-size:.8rem">Supported plants</div>', unsafe_allow_html=True)
plants = ["🍎 Apple","🫐 Blueberry","🍒 Cherry","🌽 Corn","🍇 Grape","🍊 Orange","🍑 Peach","🫑 Bell Pepper","🥔 Potato","🍓 Strawberry","🍅 Tomato","🌿 Soybean","🥒 Squash","🍓 Raspberry"]
st.markdown('<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem;padding:.5rem 0">' +
    "".join(f'<span class="pill">{p}</span>' for p in plants) +
    '</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">LeafScan AI • Built with MobileNetV2 + PlantVillage Dataset • For educational & advisory use only</div>', unsafe_allow_html=True)
