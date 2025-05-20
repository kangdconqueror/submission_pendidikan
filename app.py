import streamlit as st
import pandas as pd
import joblib
import os

# Define the directory for models
MODEL_DIR = 'model'
MODEL_FILE = os.path.join(MODEL_DIR, 'random_forest_model.pkl')
ENCODER_FILE = os.path.join(MODEL_DIR, 'label_encoder.pkl')

# --- Load Model and Encoder ---
@st.cache_resource # Cache the model to avoid reloading every time
def load_model_and_encoder():
  """Loads the trained model and label encoder."""
  if not os.path.exists(MODEL_FILE) or not os.path.exists(ENCODER_FILE):
      st.error("Model files not found. Please ensure 'random_forest_model.pkl' and 'label_encoder.pkl' are in the 'model/' directory.")
      return None, None
  try:
      loaded_model = joblib.load(MODEL_FILE)
      loaded_encoder = joblib.load(ENCODER_FILE)
      return loaded_model, loaded_encoder
  except Exception as e:
      st.error(f"Error loading model or encoder: {e}")
      return None, None

loaded_model, loaded_encoder = load_model_and_encoder()

if loaded_model is None or loaded_encoder is None:
    st.stop() # Stop the app if model loading failed

# --- Streamlit App ---
st.title('Prediksi Status Mahasiswa')

st.write("""
Aplikasi ini memprediksi status akhir mahasiswa (Graduate, Enrolled, atau Dropout)
berdasarkan input.
""")

st.header('Masukkan Data Mahasiswa:')

expected_columns = [
    'Curricular_units_2nd_sem_approved',
    'Curricular_units_2nd_sem_grade',
    'Curricular_units_1st_sem_approved',
    'Curricular_units_1st_sem_grade',
    'Tuition_fees_up_to_date',
    'Scholarship_holder',
    'Debtor',
    'Age_at_enrollment',
    'Gender', # Assuming 0=Perempuan, 1=Laki-laki based on the notebook
    'Application_mode' # This needs to be mapped correctly based on the original EDA
]

# Helper function to get the mode description (optional, for better UX)
application_modes = {
    1: '1st phase - general contingent',
    2: 'Ordinance No. 612/93',
    5: '1st phase - special contingent (Azores Island)',
    7: 'Holders of other higher courses',
    10: 'Ordinance No. 854-B/99',
    15: 'International student (bachelor)',
    16: '1st phase - special contingent (Madeira Island)',
    17: '2nd phase - general contingent',
    18: '3rd phase - general contingent',
    26: 'Ordinance No. 533-A/99, item b2) (Different Plan)',
    27: 'Ordinance No. 533-A/99, item b3 (Other Institution)',
    39: 'Over 23 years old',
    42: 'Transfer',
    43: 'Change of course',
    44: 'Technological specialization diploma holders',
    51: 'Change of institution/course',
    53: 'Short cycle diploma holders',
    57: 'Change of institution/course (International)'
}


input_data = {}

input_data['Curricular_units_2nd_sem_approved'] = st.number_input(
    'Jumlah Unit Diselesaikan Semester 2',
    min_value=0, value=10, step=1,
    help='Contoh: 15 untuk mahasiswa rajin, 2 untuk yang tidak aktif.'
)

input_data['Curricular_units_2nd_sem_grade'] = st.number_input(
    'Nilai Rata-rata Semester 2',
    min_value=0.0, max_value=20.0, value=12.0, step=0.1,
    help='Nilai skala 0–20. Contoh: 15.0 untuk aktif, 5.0 untuk tidak aktif.'
)

input_data['Curricular_units_1st_sem_approved'] = st.number_input(
    'Jumlah Unit Diselesaikan Semester 1',
    min_value=0, value=10, step=1,
    help='Contoh: 14 untuk rajin, 3 untuk yang malas.'
)

input_data['Curricular_units_1st_sem_grade'] = st.number_input(
    'Nilai Rata-rata Semester 1',
    min_value=0.0, max_value=20.0, value=12.0, step=0.1,
    help='Contoh: 14.5 untuk nilai baik, 6.0 untuk nilai rendah.'
)

input_data['Tuition_fees_up_to_date'] = st.selectbox(
    'Bayar SPP Tepat Waktu?',
    options=[1, 0],
    format_func=lambda x: 'Ya' if x == 1 else 'Tidak',
    help='1 = Ya (pembayaran lancar), 0 = Tidak (nunggak).'
)

input_data['Scholarship_holder'] = st.selectbox(
    'Penerima Beasiswa?',
    options=[1, 0],
    format_func=lambda x: 'Ya' if x == 1 else 'Tidak',
    help='1 = Ya, 0 = Tidak.'
)

input_data['Debtor'] = st.selectbox(
    'Memiliki Tunggakan?',
    options=[0, 1],
    format_func=lambda x: 'Tidak' if x == 0 else 'Ya',
    help='0 = Tidak memiliki utang, 1 = Ada tunggakan.'
)

input_data['Age_at_enrollment'] = st.number_input(
    'Usia Saat Mendaftar',
    min_value=17, max_value=70, value=20, step=1,
    help='Usia saat pertama kali mendaftar kuliah. Contoh: 19 atau 25.'
)

input_data['Gender'] = st.selectbox(
    'Gender',
    options=[0, 1],
    format_func=lambda x: 'Perempuan' if x == 0 else 'Laki-laki',
    help='0 = Perempuan, 1 = Laki-laki (berdasarkan LabelEncoder awal).'
)

selected_mode_desc = st.selectbox(
    'Mode Pendaftaran',
    options=list(application_modes.values()),
    help='Contoh: 1st phase = jalur umum, 39 = mahasiswa internasional.'
)

application_mode_id = [key for key, val in application_modes.items() if val == selected_mode_desc][0]
input_data['Application_mode'] = application_mode_id


# --- Prediction Button ---
if st.button('Prediksi Status'):
    # Create a DataFrame from the input data
    input_df = pd.DataFrame([input_data])

    # Ensure the column order matches the training data
    try:
        input_df = input_df[expected_columns]
    except KeyError as e:
        st.error(f"Error: Missing expected column(s) in input data: {e}")
        st.stop()


    # Make prediction
    try:
        prediction_encoded = loaded_model.predict(input_df)
        prediction_label = loaded_encoder.inverse_transform(prediction_encoded)

        st.subheader('Hasil Prediksi Status:')
        st.success(f"**{prediction_label[0]}**")

    except Exception as e:
        st.error(f"Error during prediction: {e}")