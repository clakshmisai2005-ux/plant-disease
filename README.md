# 🌿 LeafScan AI – Plant Disease Detector

A Streamlit web app that detects plant diseases from leaf images using a MobileNetV2 model trained on PlantVillage (38 classes, 88.89% accuracy).

---

## 📁 Required File Structure

```
your-repo/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── plant_disease_mobilenetv2.keras   ← YOUR TRAINED MODEL
└── README.md
```

---

## 🚀 Deploying to Streamlit Community Cloud (Free)

### Step 1 — Add your model to the repo
From your Colab notebook, download the model:
```python
from google.colab import files
files.download("best_plant_model.keras")
```
Rename it to `plant_disease_mobilenetv2.keras` and add it to your GitHub repository.

> ⚠️ If the model file is larger than 100 MB, use **Git LFS**:
> ```bash
> git lfs install
> git lfs track "*.keras"
> git add .gitattributes
> ```

### Step 2 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial LeafScan AI app"
git remote add origin https://github.com/YOUR_USERNAME/leafscan-ai.git
git push -u origin main
```

### Step 3 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository, branch (`main`), and main file (`app.py`)
5. Click **"Deploy!"**

Your app will be live at `https://YOUR_USERNAME-leafscan-ai-app-XXXX.streamlit.app`

---

## 🖥️ Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔄 Alternative: Use TFLite model (smaller, faster)

If you exported `model.tflite` from Colab, place it in the repo root.
The app automatically detects and uses whichever model file is present:
1. First tries `plant_disease_mobilenetv2.keras`
2. Falls back to `model.tflite`

---

## 🌿 Supported Diseases (38 classes)

| Plant | Conditions |
|-------|-----------|
| Apple | Apple Scab, Black Rot, Cedar Rust, Healthy |
| Blueberry | Healthy |
| Cherry | Powdery Mildew, Healthy |
| Corn | Gray Leaf Spot, Common Rust, Northern Blight, Healthy |
| Grape | Black Rot, Esca, Leaf Blight, Healthy |
| Orange | Huanglongbing |
| Peach | Bacterial Spot, Healthy |
| Bell Pepper | Bacterial Spot, Healthy |
| Potato | Early Blight, Late Blight, Healthy |
| Raspberry | Healthy |
| Soybean | Healthy |
| Squash | Powdery Mildew |
| Strawberry | Leaf Scorch, Healthy |
| Tomato | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria, Spider Mites, Target Spot, YLV, Mosaic Virus, Healthy |

---

## 📊 Model Details
- Architecture: MobileNetV2 (transfer learning, ImageNet weights)
- Dataset: PlantVillage (~54,000 images, 38 classes)
- Input size: 128×128 RGB
- Phase 1 accuracy: 92.8% (frozen base)
- Final test accuracy: **88.89%**
- Export format: `.keras` / `.tflite`
