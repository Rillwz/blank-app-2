import streamlit as st
import pandas as pd
from datetime import date
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

# Set up page configuration
st.set_page_config(page_title="Survei Nutrisi Harian", layout="centered")
st.title("📝 Survei Nutrisi Harian")

# Deskripsi
st.markdown("Silakan isi survei ini untuk membantu kami memahami pola makan dan kebutuhan nutrisi Anda.")

# Form input dari pengguna
with st.form("nutrition_survey"):
    st.header("1. Informasi Dasar")
    age = st.number_input("Usia", min_value=5, max_value=100, step=1)
    gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    weight = st.number_input("Berat Badan (kg)", min_value=20.0)
    height = st.number_input("Tinggi Badan (cm)", min_value=100.0)

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

    if submit:
        st.success("🎉 Jawaban berhasil disimpan. Terima kasih!")

        filename = "data_survei_nutrisi.csv"

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
            "Kalori": [total_calories]  # 👈 disimpan ke data
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

        # Tampilkan data yang disimpan hari ini
        df_input["Kalori (Prediksi)"] = int(predicted_calories)
        st.subheader("📄 Data yang disimpan:")
        st.dataframe(df_input)
