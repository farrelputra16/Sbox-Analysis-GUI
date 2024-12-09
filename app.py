import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from testlib import nonlinearity, sac, lap, dap, bic_nl, bic_sac

# Fungsi untuk menunjukkan hasil
def show_result(test_name, value):
    st.success(f"{test_name}: *{value:.5f}*")
    return pd.DataFrame({"Metric": [test_name], "Value": [value]})

# Fungsi untuk mengolah semua jenis uji
def handle_test_type(test_type, sbox):
    test_functions = {
        "Non-Linearity (NL)": lambda sbox: nonlinearity(sbox, 8, 8), 
        "Strict Avalanche Criterion (SAC)": lambda sbox: sac(sbox, 8),
        "BIC - NL": lambda sbox: bic_nl(sbox, 8),
        "BIC - SAC": lambda sbox: bic_sac(sbox),
        "Linear Approximation Probability (LAP)": lambda sbox: lap(sbox, 8),
        "Differential Approximation Probability (DAP)": lambda sbox: dap(sbox, 8),
    }

    if test_type == "Uji Semua":
        result_df = pd.DataFrame(columns=["Metric", "Value"])  
        for test_name, func in test_functions.items():
            value = func(sbox)
            result_df = pd.concat([result_df, show_result(test_name, value)], ignore_index=True)
        return result_df
    elif test_type in test_functions:
        value = test_functions[test_type](sbox)
        result_df = show_result(test_type, value)
        return result_df
    else:
        st.error("Test type not recognized.")
        return None

# Fungsi Ekspor Data ke Excel
def export_to_excel(data, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name="S-Box Results")
    processed_data = output.getvalue()
    return processed_data

# Streamlit GUI
st.set_page_config(page_title="S-Box Analysis", page_icon="🔐", layout="wide")

# Menambahkan latar belakang dan animasi
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #00c6ff, #0072ff);
            font-family: 'Roboto', sans-serif;
            color: #fff;
            margin: 0;
            padding: 0;
        }
        .header {
            text-align: center;
            padding: 50px;
            animation: slideIn 1.5s ease-out;
        }
        .header h1 {
            font-size: 50px;
            color: #fff;
        }
        .header p {
            font-size: 20px;
            color: #d3d3d3;
        }
        @keyframes slideIn {
            0% { transform: translateY(-50px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }
        .stButton > button {
            background-color: #ff8c00;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            padding: 10px 30px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #ff6000;
            transform: scale(1.05);
        }
        .stRadio > div {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            margin: 10px 0;
            padding: 15px;
            transition: background-color 0.3s ease;
        }
        .stRadio > div:hover {
            background-color: rgba(255, 255, 255, 0.3);
        }
        .stTextArea > div {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Header dengan animasi
st.markdown('<div class="header"><h1>S-Box Analysis GUI</h1><p>Uji keamanan S-Box dengan berbagai metriks pengujian</p></div>', unsafe_allow_html=True)

# Pilih Input Data
data_input_method = st.radio(
    "Pilih metode input data:",
    ["Manual Input", "Upload File (.xlsx)"],
    label_visibility="collapsed"
)

# Kolom untuk Input dan Pilih Jenis Pengujian
col1, col2 = st.columns([2, 1])

with col1:
    if data_input_method == "Manual Input":
        sbox_input = st.text_area(
            "Masukkan S-Box (Format: 256 int (0-255), pisahkan dengan koma):",
            height=150,
            help="Masukkan nilai S-Box dalam format angka antara 0 dan 255, pisahkan dengan koma"
        )
    elif data_input_method == "Upload File (.xlsx)":
        uploaded_file = st.file_uploader("Upload file Excel berisi S-Box:", type=["xlsx"])
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file, header=None)
                st.write("Data S-Box yang diimport:")
                st.dataframe(df)
                sbox_input = ",".join(map(str, df.to_numpy().flatten()))
            except Exception as e:
                st.error(f"Terjadi kesalahan dalam membaca file: {str(e)}")

with col2:
    test_type = st.radio(
        "Pilih jenis pengujian:",
        ["Non-Linearity (NL)", "Strict Avalanche Criterion (SAC)", "BIC - NL", "BIC - SAC", "Linear Approximation Probability (LAP)", "Differential Approximation Probability (DAP)", "Uji Semua"],
        label_visibility="collapsed"
    )

# Menjalankan pengujian saat tombol ditekan
if st.button("Jalankan Pengujian"):
    try:
        if not sbox_input:
            st.error("Input S-Box tidak boleh kosong!")
        else:
            sbox = list(map(int, sbox_input.split(",")))
            if len(sbox) != 256:
                st.error("S-Box harus memiliki panjang 256!")
            else:
                result_df = handle_test_type(test_type, sbox)

                # Menampilkan hasil dalam tabel
                st.write("Hasil Pengujian:", unsafe_allow_html=True)
                st.dataframe(result_df, use_container_width=True)

                # Menyediakan opsi untuk mengunduh hasil
                excel_data = export_to_excel(result_df, "sbox_results.xlsx")
                st.download_button(
                    label="Unduh Hasil sebagai Excel",
                    data=excel_data,
                    file_name="sbox_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")

# Footer
st.markdown("""
    <div style='text-align: center; color: #d3d3d3; font-size: 14px; padding-top: 20px;'>
        <p>📚 Kelompok 7 Kriptografi Rombel 3 TI 22</p>aa
    </div>
""", unsafe_allow_html=True)
