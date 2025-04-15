import streamlit as st
import pandas as pd
from datetime import date
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

from PIL import Image

import os

import google.generativeai as genai

from dotenv import load_dotenv, dotenv_values  # we can use load_dotenv or dotenv_values both perform the same task

load_dotenv()

genai.configure(api_key="AIzaSyDn_CGmV5WeE3bu6oSrVDzcen67bqPEhAg") 

# Set up page configuration
st.set_page_config(page_title="EatWise", layout="centered")
st.title("📝 EatWiseEveryday")

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 1024,
}

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧾 Isi Survei", "📊 Lihat Dataset", "📈 Prediksi Pola Kalori", "📷 Find Calories", "📷 Find Calories"])

filename = "data_survei_nutrisi.csv"

with tab1:
    with st.form("nutrition_survey"):
        st.header("1. Informasi Dasar")
        nim = st.text_input("NIM", max_chars=11, placeholder="Nomor Induk Mahasiswa!")  # Input NIM
        # Check if NIM is provided
        if not nim:
            st.error("NIM is required!")
        
        age = st.number_input("Usia", max_value=100, step=1)
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        weight = st.number_input("Berat Badan (kg)")
        height = st.number_input("Tinggi Badan (cm)")

        st.header("2. Frekuensi Konsumsi Harian (Per Hari)")
        nasi = st.slider("🍚 Konsumsi Nasi", 0, 5, 2)
        nasi_calories_per_serving = st.number_input("Kalori / Porsi Nasi (default)", value=130, step=10)

        sayur = st.slider("🥦 Konsumsi Sayuran", 0, 5, 2)
        sayur_calories_per_serving = st.number_input("Kalori / Porsi Sayuran (default)", value=50, step=10)

        buah = st.slider("🍎 Konsumsi Buah", 0, 5, 1)
        buah_calories_per_serving = st.number_input("Kalori / Porsi Buah (default)", value=80, step=10)

        daging = st.slider("🍗 Konsumsi Daging/Protein Hewani", 0, 5, 1)
        daging_calories_per_serving = st.number_input("Kalori per Porsi Daging (default)", value=250, step=10)

        susu = st.slider("🥛 Konsumsi Susu/Sumber Kalsium", 0, 5, 0)
        susu_calories_per_serving = st.number_input("Kalori / Porsi Susu (default)", value=150, step=10)

        air = st.number_input("💧 Konsumsi Air (liter)", 0.0, 5.0, 1.5, step=0.1)

        submit = st.form_submit_button("Kirim Jawaban")

        if nim and submit:
            st.success("🎉 Jawaban berhasil disimpan. Terima kasih!")
            
            # Data yang baru diinput pengguna
            total_calories = (
                10 * weight +
                6.25 * height - 
                5 * age +
                (5 if gender == "Laki-laki" else -161)
            ) + (
                nasi * nasi_calories_per_serving +
                daging * daging_calories_per_serving +
                susu * susu_calories_per_serving +
                sayur * sayur_calories_per_serving +
                buah * buah_calories_per_serving
            )

            survey_data = {
                "NIM": [nim],  # Save NIM
                "Tanggal": [date.today()],
                "Usia": [age],
                "Jenis Kelamin": [gender],
                "Berat Badan": [weight],
                "Tinggi Badan": [height],
                "Nasi": [nasi],
                "Sayur": [sayur],
                "Buah": [buah],
                "Daging": [daging],
                "Susu": [susu],
                "Air (L)": [air],
                "Kalori": [total_calories]
            }
            df_input = pd.DataFrame(survey_data)

            # Gabungkan data baru ke dataset lama (jika ada)
            if os.path.exists(filename):
                df_existing = pd.read_csv(filename)
                df_combined = pd.concat([df_existing, df_input], ignore_index=True)
            else:
                df_combined = df_input

            # Hitung Kalori jika belum ada
            if "Kalori" not in df_combined.columns:
                df_combined["Kalori"] = (
                    10 * df_combined["Berat Badan"] +
                    6.25 * df_combined["Tinggi Badan"] -
                    5 * df_combined["Usia"] +
                    df_combined["Jenis Kelamin"].map({"Laki-laki": 5, "Perempuan": -161})
                ) + (
                    df_combined["Nasi"] * nasi_calories_per_serving +
                    df_combined["Daging"] * daging_calories_per_serving +
                    df_combined["Susu"] * susu_calories_per_serving +
                    df_combined["Sayur"] * sayur_calories_per_serving +
                    df_combined["Buah"] * buah_calories_per_serving
                )

            # Simpan data kembali ke file
            df_combined.to_csv(filename, index=False)

            # Latih model dengan data terbaru
            df = df_combined.dropna(subset=["Kalori"]).copy()
            df["Gender_encoded"] = LabelEncoder().fit_transform(df["Jenis Kelamin"])

            features = ["Usia", "Gender_encoded", "Berat Badan", "Tinggi Badan",
                        "Nasi", "Sayur", "Buah", "Daging", "Susu", "Air (L)"]
            X = df[features]
            y = df["Kalori"]

            # Prediksi dengan model jika datanya valid
            if len(X) > 0 and len(X) == len(y):
                model = LinearRegression()
                model.fit(X, y)

                gender_encoded = 0 if gender == "Laki-laki" else 1
                user_data = [[age, gender_encoded, weight, height, nasi, sayur, buah, daging, susu, air]]
                predicted_calories = model.predict(user_data)[0]
            else:
                predicted_calories = None

            # Jika model gagal, pakai rumus tetap
            if predicted_calories is None:
                predicted_calories = (
                    10 * weight +
                    6.25 * height -
                    5 * age +
                    (5 if gender == "Laki-laki" else -161)
                ) + (
                    nasi * nasi_calories_per_serving +
                    daging * daging_calories_per_serving +
                    susu * susu_calories_per_serving +
                    sayur * sayur_calories_per_serving +
                    buah * buah_calories_per_serving
                )
            
            # Tampilkan hasil prediksi
            st.write(f"🔍 Prediksi kebutuhan kalori Anda (Regresi Linear): **{int(predicted_calories)} kcal/hari**")

            # Tampilkan juga kalkulasi tetap
            fixed_calories = (
                10 * weight +
                6.25 * height -
                5 * age +
                (5 if gender == "Laki-laki" else -161)
            ) + (
                nasi * nasi_calories_per_serving +
                daging * daging_calories_per_serving +
                susu * susu_calories_per_serving +
                sayur * sayur_calories_per_serving +
                buah * buah_calories_per_serving
            )
            st.write(f"📊 Total kalori Anda (Rumus Tetap): **{int(fixed_calories)} kcal/hari**")


with tab2:
    st.subheader("📊 Dataset Survei Nutrisi")

    # Expander untuk reset dataset
    with st.expander("🔒 Reset Dataset (Masukkan PIN)"):
        reset_pin = st.text_input("Masukkan PIN", type="password", placeholder="Masukkan PIN rahasia...")

        col1, col2 = st.columns([1, 4])
        with col1:
            reset_click = st.button("Reset")
        if reset_click:
            correct_pin = "RAFA"
            if reset_pin == correct_pin:
                if os.path.exists(filename):
                    os.remove(filename)
                    st.success("✅ Dataset berhasil di-reset.")
                else:
                    st.warning("⚠️ Dataset tidak ditemukan.")
            else:
                st.error("❌ PIN salah. Coba lagi.")

    # Tampilkan dataset jika ada
    if os.path.exists(filename):
        df_all = pd.read_csv(filename)
        st.dataframe(df_all, use_container_width=True, hide_index=True)

        st.download_button(
            label="Unduh Dataset sebagai CSV",
            data=df_all.to_csv(index=False),
            file_name="data_survei_nutrisi.csv",
            mime="text/csv"
        )

with tab3:
    st.markdown("---")
    st.subheader("📈 Prediksi Pola Kalori dengan ARIMA")
    
    if os.path.exists(filename):
        df_all = pd.read_csv(filename)
        df_all['Tanggal'] = pd.to_datetime(df_all['Tanggal'])

        if len(df_all["NIM"].unique()) > 0:
            selected_nim = st.selectbox("🔍 Pilih NIM untuk Diprediksi", df_all["NIM"].unique())
            df_nim = df_all[df_all["NIM"] == selected_nim].copy()

            if not df_nim.empty and len(df_nim) >= 5:
                df_nim = df_nim.sort_values(by="Tanggal").reset_index(drop=True)
                kalori_series = df_nim["Kalori"]
                kalori_series.index = range(1, len(kalori_series) + 1)

                st.line_chart(kalori_series.rename("Kalori per Entry"))

                with st.expander("⚙️ Atur Parameter ARIMA (opsional)"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        p = st.number_input("ARIMA p", min_value=0, max_value=5, value=1)
                    with col2:
                        d = st.number_input("ARIMA d", min_value=0, max_value=2, value=1)
                    with col3:
                        q = st.number_input("ARIMA q", min_value=0, max_value=5, value=1)
                    with col4:
                        future_steps = st.number_input("Jumlah Prediksi", min_value=1, max_value=30, value=5)

                try:
                    model = ARIMA(kalori_series, order=(p, d, q))
                    model_fit = model.fit()
                    forecast = model_fit.forecast(steps=future_steps)

                    forecast_index = range(len(kalori_series) + 1, len(kalori_series) + 1 + future_steps)
                    forecast_series = pd.Series(forecast, index=forecast_index)

                    st.markdown("### 📊 Visualisasi Prediksi Kalori")
                    fig, ax = plt.subplots()
                    kalori_series.plot(ax=ax, label="Kalori Historis", marker='o')
                    forecast_series.plot(ax=ax, label="Prediksi", marker='x', color="red")
                    ax.set_xlabel("Entry ke-")
                    ax.set_ylabel("Kalori")
                    ax.legend()
                    st.pyplot(fig)

                    forecast_df = pd.DataFrame({
                        "Entry ke-": forecast_index,
                        "Prediksi Kalori": forecast
                    })
                    st.dataframe(forecast_df, use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan saat menjalankan ARIMA: {e}")
            elif len(df_nim) < 5:
                st.warning("⚠️ NIM ini belum memiliki cukup data untuk prediksi. Minimal 5 entri diperlukan.")
            else:
                st.info("ℹ️ Tidak ada data yang tersedia untuk NIM yang dipilih.")
        else:
            st.info("ℹ️ Belum ada data NIM yang tersedia.")

with tab4:
    
    st.title("Find Object Calories 🔍")
    
    disclaimer_message = """This is a object detector model so preferably use images containing different objects,tools... for best results 🙂"""

    # Hide the disclaimer initially
    st.write("")

    # Show the disclaimer if the button is clicked
    with st.expander("Disclaimer ⚠️", expanded=False):
       st.markdown(disclaimer_message)
    
    # Upload image through Streamlit
    uploaded_image = st.file_uploader("Choose an image ...", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        # Display the uploaded image
        st.image(uploaded_image, caption="Uploaded Image.", use_container_width=True)

        # Process the image (example: get image dimensions) buat dengan Camera
        #image = Image.open(picture)

        # Process the image (example: get image dimensions) buat dengan Camera
        image = Image.open(uploaded_image)

        if st.button("Identify the objects"):

            st.success("Analyzing image...")

            vision_model = genai.GenerativeModel('gemini-1.5-flash')

            response = vision_model.generate_content([
                "From the image, list all recognizable food items along with an estimated calorie count for a typical serving. Format the result as a table with two columns: Food Item and Estimated Calories.",
                image
            ])
            
            st.write("### Food Items and Estimated Calories:")
            st.markdown(response.text)

            st.success("Thanks for visiting 🤩!!")
            st.info("Upload another image if you'd like to try again 😄!")

with tab5:
    st.title("Camera Calories 🔍")

    enable = st.checkbox("Enable camera")
    picture = st.camera_input("Take a picture", disabled=not enable)

    if picture is not None:
        image = Image.open(picture)

        if st.button("Identify the objects"):
            st.success("Analyzing image...")
            vision_model = genai.GenerativeModel('gemini-1.5-flash')
            response = vision_model.generate_content([
                "From the image, list all recognizable food items along with an estimated calorie count for a typical serving. Format the result as a table with two columns: Food Item and Estimated Calories.",
                image
            ])

            st.write("### Food Items and Estimated Calories:")
            st.markdown(response.text)
            st.success("Thanks for visiting 🤩!!")
            st.info("Upload another image if you'd like to try again 😄!")
    else:
        st.info("Please enable the camera and take a picture first.")
