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
        background-color: #1a1a2e;
        font-family: 'Press Start 2P', cursive;
        color: #e0e0e0;
        overflow-x: hidden;
    }

    /* Pixel Art Border */
    .pixel-border {
        border: 4px solid #4a4e69;
        border-image: 
            repeating-linear-gradient(
                45deg, 
                #4a4e69 0, 
                #4a4e69 2px, 
                transparent 2px, 
                transparent 10px
            ) 1;
        box-shadow: 0 0 10px rgba(74, 78, 105, 0.5);
    }

    /* Pixel Button Styles */
    .pixel-button {
        background-color: #6a4c93;
        color: #ffffff;
        border: 2px solid #392b58;
        font-family: 'Press Start 2P';
        text-transform: uppercase;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .pixel-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            120deg, 
            transparent, 
            rgba(255,255,255,0.3), 
            transparent
        );
        transition: all 0.5s;
    }

    .pixel-button:hover::before {
        left: 100%;
    }

    /* Pixel Input Styles */
    .pixel-input {
        background-color: #16213e;
        border: 2px solid #0f3460;
        color: #e94560;
        font-family: 'Press Start 2P';
        font-size: 12px;
    }

    /* Pixel Radio Styles */
    .pixel-radio {
        background-color: #0f3460;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }

    /* Pixel Animation */
    @keyframes pixelate {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .pixel-animate {
        animation: pixelate 1.5s infinite;
    }

    /* Retro Scan Line Effect */
    .scan-line {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background: 
            repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.15),
                rgba(0, 0, 0, 0.15) 1px,
                transparent 1px,
                transparent 2px
            );
        z-index: 9999;
    }
    .sbox-input textarea {
        background-color: #16213e !important; 
        color: #e94560 !important; 
        border: 3px solid #0f3460 !important; 
        font-family: 'Press Start 2P', monospace !important;
        font-size: 10px !important;
        padding: 10px !important;
        border-radius: 5px !important;
        box-shadow: 
            inset 0 0 10px rgba(233,69,96,0.2),
            0 0 15px rgba(15,52,96,0.3) !important;
        text-shadow: 1px 1px 2px rgba(233,69,96,0.3) !important;
        line-height: 1.5 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
    }

    .sbox-input textarea:focus {
        outline: none !important;
        border-color: #e94560 !important;
        box-shadow: 
            0 0 15px rgba(233,69,96,0.5),
            inset 0 0 10px rgba(15,52,96,0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="scan-line"></div>
""", unsafe_allow_html=True)

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Modifikasi header
st.markdown("""
    <div class="header pixel-animate" style="text-align: center;">
        <h1 style="font-family: 'Press Start 2P'; color: #e94560; text-align: center;">
            🔒 S-Box Crypto Analyzer
        </h1>
        <p style="font-family: 'Press Start 2P'; color: #4a4e69; text-align: center;">
            Retro Cryptographic Evaluation
        </p>
    </div>
""", unsafe_allow_html=True)


data_input_method = st.radio(
    "Pilih metode input data:",
    ["Manual Input", "Upload File (.xlsx)"],
    label_visibility="collapsed",
    key="input_method",
    help="Select your data input method"
)

# Kolom untuk Input dan Pilih Jenis Pengujian
col1, col2 = st.columns([2, 1])

with col1:
    if data_input_method == "Manual Input":
        sbox_input = st.text_area(
    "Masukkan S-Box (Format: 256 int (0-255), pisahkan dengan koma):",
    height=150,
    help="Input S-Box values separated by comma",
    key="sbox_input",
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
        <p>📚 Kelompok 7 Kriptografi Rombel 3 TI 22</p>
    </div>
""", unsafe_allow_html=True)
