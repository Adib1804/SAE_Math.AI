import streamlit as st
from sympy import sympify, Rational, simplify
import uuid
import os
import re

st.set_page_config(page_title="SAE Math.AI", layout="wide")

# ---------- Fungsi Matematik ----------
def solve_math_problem(question):
    try:
        question = question.lower().strip()

        # Gantikan perkataan dengan simbol matematik
        replacements = {
            "tambah": "+",
            "tolak": "-",
            "darab": "*",
            "bahagi": "/",
            "peratus": "/100",
            "per": "/", 
            "bundar kepada": "bundar",  
        }

        for word, symbol in replacements.items():
            question = question.replace(word, symbol)

        # Bundarkan
        if "bundar" in question:
            nombor = re.findall(r"[-+]?\d*\.\d+|\d+", question)
            if nombor:
                dibundar = round(float(nombor[0]))
                return str(dibundar), f"Nombor {nombor[0]} dibundarkan menjadi {dibundar}."
            else:
                return None, None

        # Tangani pecahan seperti '1/2'
        pecahan = re.findall(r'\d+\s*/\s*\d+', question)
        for f in pecahan:
            question = question.replace(f, f.replace(" ", ""))

        # Nisbah: Pemudahan atau pengiraan nilai
        if "nisbah" in question or ":" in question:
            numbers = re.findall(r"\d+", question)
    
        if "jumlah" in question and len(numbers) >= 3:
            a, b, total = map(int, numbers[:3])
            total_parts = a + b
            part_value = total / total_parts
            part_a = part_value * a
            part_b = part_value * b
            explanation = (
                f"Nisbah {a}:{b} bermakna jumlah bahagian = {a}+{b} = {total_parts}.\n"
                f"Setiap bahagian bernilai {total} ÷ {total_parts} = {part_value:.2f}.\n"
                f"Jadi: Bahagian pertama = {a} x {part_value:.2f} = {part_a:.2f}, "
                f"Bahagian kedua = {b} x {part_value:.2f} = {part_b:.2f}."
            )
            return f"{int(part_a)} dan {int(part_b)}", explanation

        elif len(numbers) == 3:
            a, b, known = map(int, numbers)
            if "pertama" in question or "lelaki" in question:
                multiplier = known / a
                second = multiplier * b
                explanation = (
                    f"Nisbah {a}:{b} dengan nilai pertama = {known}.\n"
                    f"1 bahagian = {known} ÷ {a} = {multiplier:.2f}.\n"
                    f"Bahagian kedua = {b} x {multiplier:.2f} = {second:.2f}"
                )
                return f"{int(second)}", explanation
            elif "kedua" in question or "perempuan" in question:
                multiplier = known / b
                first = multiplier * a
                explanation = (
                    f"Nisbah {a}:{b} dengan nilai kedua = {known}.\n"
                    f"1 bahagian = {known} ÷ {b} = {multiplier:.2f}.\n"
                    f"Bahagian pertama = {a} x {multiplier:.2f} = {first:.2f}"
                )
                return f"{int(first)}", explanation

        elif len(numbers) == 2:
            a, b = map(int, numbers)
            from math import gcd
            g = gcd(a, b)
            return f"{a//g}:{b//g}", f"Nisbah {a}:{b} dipermudahkan jadi {a//g}:{b//g}"

        # Cuba nilai guna sympy
        jawapan = sympify(question)
        penjelasan = f"Langkah pengiraan: {question} = {jawapan}"
        return str(jawapan), penjelasan

    except Exception as e:
        return None, None



# ---------- Fungsi Paparan Mesej ----------
def paparkan_perbualan():
    for msg in st.session_state.chat_history:
        with st.container():
            if msg["role"] == "user":
                st.markdown(f"<div style='text-align:right;color:#2c7be5;'><b>🧑 {msg['content']}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:left;color:#10b981;'><b>🤖 {msg['content']}</b></div>", unsafe_allow_html=True)

# ---------- Fungsi Sidebar ----------
def paparkan_sidebar():
    st.sidebar.markdown("## 📁 Log Perbualan")
    for title in st.session_state.chat_titles:
        if st.sidebar.button(title, key=title):
            st.session_state.chat_history = st.session_state.saved_chats[title]

    if st.sidebar.button("➕ Chat Baharu"):
        st.session_state.chat_history = []
        new_id = str(uuid.uuid4())
        st.session_state.chat_titles.append(f"Perbualan {len(st.session_state.chat_titles)+1}")
        st.session_state.saved_chats[f"Perbualan {len(st.session_state.chat_titles)}"] = []

# ---------- Fungsi Utama ----------
def main():
    # Logo dan nama AI di atas
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("logo.png", width=60)
    with col2:
        st.markdown("<h1 style='margin-bottom: 0;'>SAE Math.AI</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

    # Inisialisasi sesi
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_titles" not in st.session_state:
        st.session_state.chat_titles = []
    if "saved_chats" not in st.session_state:
        st.session_state.saved_chats = {}

    # Sidebar
    paparkan_sidebar()

    # Paparan perbualan
    st.markdown("### 💬 Perbualan")
    paparkan_perbualan()

    # Kotak mesej di bahagian bawah
    question = st.chat_input("Tanyalah saya")
    if question:
        # Simpan tajuk jika pertama kali
        if len(st.session_state.chat_history) == 0:
            tajuk_auto = question.strip()[:30]
            if len(tajuk_auto) == 30:
                tajuk_auto += "..."
            st.session_state.chat_titles.append(tajuk_auto)
            st.session_state.saved_chats[tajuk_auto] = []

        # Simpan soalan pengguna
        st.session_state.chat_history.append({"role": "user", "content": question})

        # Dapatkan jawapan AI
        jawapan, penjelasan = solve_math_problem(question)
        if jawapan is not None and penjelasan is not None:
            st.session_state.chat_history.append({"role": "ai", "content": jawapan + "\n\n" + penjelasan})
        else:
            st.session_state.chat_history.append({"role": "ai", "content": "Maaf, saya tidak dapat menyelesaikan soalan ini."})


        # Simpan perbualan dalam log
        if len(st.session_state.chat_titles) > 0:
            tajuk_terkini = st.session_state.chat_titles[-1]
            st.session_state.saved_chats[tajuk_terkini] = st.session_state.chat_history

# ---------- Mula Aplikasi ----------
if __name__ == "__main__":
    main()
