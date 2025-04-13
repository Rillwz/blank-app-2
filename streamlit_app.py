import streamlit as st
import pandas as pd
from datetime import date
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import os

# Set up page configuration
st.set_page_config(page_title="Survei Nutrisi Kalori", layout="centered")
st.title("📝 Survei Nutrisi Kalori")

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
    sayur = st.slider("🥦 Konsumsi Sayuran", 0, 5, 2)
    buah = st.slider("🍎 Konsumsi Buah", 0, 5, 1)
    daging = st.slider("🍗 Konsumsi Daging/Protein Hewani", 0, 5, 1)
    susu = st.slider("🥛 Konsumsi Susu/Sumber Kalsium", 0, 5, 0)
    air = st.number_input("💧 Konsumsi Air (liter)", 0.0, 5.0, 1.5, step=0.1)

    submit = st.form_submit_button("Kirim Jawaban")

    if submit:
        st.success("🎉 Jawaban berhasil disimpan. Terima kasih!")

        # Kalkulasi kalori dengan rumus tetap (fixed)
        if gender == "Laki-laki":
            fixed_calories = (
                10 * weight + 
                6.25 * height - 
                5 * age + 
                5  # untuk pria
            ) + (nasi * 130 + daging * 200 + susu * 70)  # Kalori per porsi untuk setiap makanan
        else:
            fixed_calories = (
                10 * weight + 
                6.25 * height - 
                5 * age - 
                161  # untuk wanita
            ) + (nasi * 130 + daging * 200 + susu * 70)  # Kalori per porsi untuk setiap makanan


        # Simpan data survei lengkap
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
            "Kalori": [int(fixed_calories)]  # Simpan kalori yang fixed
        }

        df_input = pd.DataFrame(survey_data)

        filename = "data_survei_nutrisi.csv"

        # Simpan ke file CSV
        if not os.path.exists(filename):
            df_input.to_csv(filename, index=False)
        else:
            df_input.to_csv(filename, mode='a', header=False, index=False)

        # Tampilkan hasil kalori fixed
        st.write(f"🔍 Kebutuhan kalori Anda berdasarkan rumus tetap: **{int(fixed_calories)} kcal/hari**")

        # Jika ingin menambahkan model Linear Regression:
        # 1. Gunakan data yang sudah ada untuk melatih model Linear Regression
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df = df.dropna(subset=["Kalori"])

            # Menambahkan encoding untuk gender
            df["Gender_encoded"] = LabelEncoder().fit_transform(df["Jenis Kelamin"])

            features = ["Usia", "Gender_encoded", "Berat Badan", "Tinggi Badan", 
                        "Nasi", "Sayur", "Buah", "Daging", "Susu", "Air (L)"]
            X = df[features]
            y = df["Kalori"]

            model = LinearRegression()
            model.fit(X, y)

            gender_encoded = 0 if gender == "Laki-laki" else 1
            user_data = [[age, gender_encoded, weight, height, nasi, sayur, buah, daging, susu, air]]
            predicted_calories = model.predict(user_data)[0]

            # Tampilkan hasil prediksi dari model Linear Regression
            st.write(f"🔍 Prediksi kebutuhan kalori berdasarkan model Linear Regression: **{int(predicted_calories)} kcal/hari**")

        # Pesan apakah kalori normal
        if gender == "Laki-laki":
            if predicted_calories < 2000:
                status = "di bawah normal untuk pria dengan aktivitas rendah."
            elif predicted_calories > 3200:
                status = "di atas normal untuk pria sangat aktif."
            else:
                status = "tergolong normal untuk pria."
        else:
            if predicted_calories < 1600:
                status = "di bawah normal untuk wanita dengan aktivitas rendah."
            elif predicted_calories > 2600:
                status = "di atas normal untuk wanita sangat aktif."
            else:
                status = "tergolong normal untuk wanita."

        st.info(f"📊 Berdasarkan estimasi umum, kebutuhan kalori Anda **{status}**")