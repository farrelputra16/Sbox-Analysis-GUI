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
    # Daftar tes dengan parameter
    test_functions = {
        "Non-Linearity (NL)": lambda sbox: nonlinearity(sbox, 8, 8),  # NL dengan 3 parameter
        "Strict Avalanche Criterion (SAC)": lambda sbox: sac(sbox, 8),
        "BIC - NL": lambda sbox: bic_nl(sbox, 8),
        "BIC - SAC": lambda sbox: bic_sac(sbox),
        "Linear Approximation Probability (LAP)": lambda sbox: lap(sbox, 8),
        "Differential Approximation Probability (DAP)": lambda sbox: dap(sbox, 8),
    }

     # Jika test_type adalah "Uji Semua", jalankan semua tes
    if test_type == "Uji Semua":
        result_df = pd.DataFrame(columns=["Metric", "Value"])  # Inisialisasi DataFrame kosong
        for test_name, func in test_functions.items():
            # Jalankan fungsi tes dan tampilkan hasil
            value = func(sbox)
            result_df = pd.concat([result_df, show_result(test_name, value)], ignore_index=True)
        return result_df

    # Jika test_type ada dalam daftar, jalankan tes yang sesuai
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
st.title("S-Box Analysis GUI")
st.write("Aplikasi ini digunakan untuk menguji keamanan S-Box dengan menggunakan berbagai macam metriks pengujian dan terdapat pilihan inputan teks normal maupun file berformat .xlxs")

# Pilih Input Data
data_input_method = st.radio(
    "Pilih metode input data:",
    ["Manual Input", "Upload File (.xlsx)"]
)

if data_input_method == "Manual Input":
    # Input Manual
    sbox_input = st.text_area(
        "Masukkan S-Box (Format: 256 int (0-255), pisahkan dengan koma):",
        height=150,
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

# Pilih jenis pengujian
test_type = st.radio(
    "Pilih jenis pengujian:",
    ["Non-Linearity (NL)", "Strict Avalanche Criterion (SAC)","BIC - NL","BIC - SAC","Linear Approximation Probability (LAP)","Differential Approximation Probability (DAP)","Uji Semua"]
)

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
                st.write("Hasil pengujian:")
                st.dataframe(result_df)

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

st.markdown("""
    <h2 style='text-align: center; color: gray; font-size: 20px;'>Kelompok 7 Kriptografi Rombel 3 TI 22</h2>
""", unsafe_allow_html=True)