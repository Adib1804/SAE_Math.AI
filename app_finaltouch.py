import streamlit as st
from sympy import sympify, simplify, Rational
import re
from datetime import datetime
import uuid

# ------ Fungsi: Logik Penyelesaian Soalan ------
def kira_soalan(soalan):
    try:
        # Bersihkan dan kenal pasti bentuk input
        soalan = soalan.lower().strip()
        penjelasan = ""
        jawapan = ""

        # Pecahan (contoh: 1/2 + 3/4)
        if re.search(r'\d+/\d+', soalan):
            pecahan = re.findall(r'\d+/\d+', soalan)
            operasi = None
            if "tambah" in soalan or "+" in soalan:
                operasi = "+"
            elif "tolak" in soalan or "-" in soalan:
                operasi = "-"
            elif "darab" in soalan or "*" in soalan:
                operasi = "*"
            elif "bahagi" in soalan or "/" in soalan:
                operasi = "/"

            if operasi and len(pecahan) >= 2:
                f1 = Rational(pecahan[0])
                f2 = Rational(pecahan[1])
                hasil = eval(f"f1 {operasi} f2")
                penjelasan = f"Langkah: {f1} {operasi} {f2} = {hasil}"
                jawapan = str(hasil)

        # Perpuluhan
        elif re.search(r'\d+\.\d+', soalan):
            expr = re.sub(r'[^\d\.\+\-\*/]', '', soalan)
            hasil = eval(expr)
            penjelasan = f"Langkah: {expr} = {hasil}"
            jawapan = str(round(hasil, 2))

        # Peratus
        elif "%" in soalan or "peratus" in soalan:
            match = re.search(r'(\d+)%?\s*(daripada|of)?\s*(\d+)', soalan)
            if match:
                p = float(match.group(1)) / 100
                n = float(match.group(3))
                hasil = p * n
                penjelasan = f"Langkah: {match.group(1)}% x {n} = {hasil}"
                jawapan = str(round(hasil, 2))

        # Nisbah
        elif ":" in soalan or "nisbah" in soalan:
            match = re.findall(r'\d+', soalan)
            if len(match) >= 2:
                r1, r2 = int(match[0]), int(match[1])
                penjelasan = f"Nisbah ialah {r1}:{r2}"
                jawapan = f"{r1}:{r2}"

        # Pembundaran
        elif "bundar" in soalan or "pembundaran" in soalan:
            match = re.search(r'(\d+)(?:\.\d+)?', soalan)
            if match:
                num = float(match.group(1))
                jawapan = str(round(num))
                penjelasan = f"Langkah: Bundarkan {num} kepada {jawapan}"

        # Operasi biasa
        else:
            expr = re.sub(r'[^\d\.\+\-\*/]', '', soalan)
            hasil = eval(expr)
            penjelasan = f"Langkah: {expr} = {hasil}"
            jawapan = str(hasil)

        return jawapan, penjelasan

    except Exception:
        return "Maaf, saya tidak dapat menyelesaikan soalan ini.", ""

# ------ Fungsi: Jana Tajuk ------
def jana_tajuk(soalan):
    return soalan[:30].capitalize() + ("..." if len(soalan) > 30 else "")

# ------ Streamlit App ------
st.set_page_config(layout="wide")
st.markdown("<style>footer{visibility:hidden;}</style>", unsafe_allow_html=True)

# ------ Sidebar ------
with st.sidebar:
    st.title("📁 Chat Baharu")
    if st.sidebar.button("+ Chat Baharu"):
        st.session_state.chat_history = []
        st.session_state.logs.append({
            "id": str(uuid.uuid4()),
            "title": "Chat Baharu",
            "timestamp": datetime.now(),
            "history": []
        })
        st.session_state.rerun_triggered = False
        st.rerun()

    st.markdown("---")
    st.subheader("🕓 Log Perbualan")
    for i, log in enumerate(st.session_state.get("logs", [])):
        if st.button(log["title"], key=f"log_{i}"):
            st.session_state.chat_history = log["history"]
            st.rerun()

# ------ Inisialisasi Session ------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "logs" not in st.session_state:
    st.session_state.logs = []

# ------ Header Atas ------
col1, col2 = st.columns([1, 8])
with col1:
    st.image("logo.png", width=60)
with col2:
    st.markdown("## SAE Math.AI")

st.markdown("---")  # Garis pemisah

# ------ Ruangan Paparan Chat ------
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        align = "left" if msg["role"] == "ai" else "right"
        bg = "#f0f0f0" if msg["role"] == "ai" else "#d1e7dd"
        st.markdown(
            f"""
            <div style="text-align: {align}; background-color: {bg}; padding:10px; margin:10px; border-radius: 10px;">
                {msg["content"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ------ Input Pengguna (di bawah) ------
with st.container():
    user_input = st.text_input("Tanyalah saya", placeholder="Contoh: Berapakah 1/2 tambah 3/4?", key="input")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        jawapan, penjelasan = kira_soalan(user_input)
        st.session_state.chat_history.append({"role": "ai", "content": jawapan + "\n\n" + penjelasan})

        # Update tajuk automatik pada log perbualan pertama
        if len(st.session_state.logs) == 0:
            st.session_state.logs.append({
                "id": str(uuid.uuid4()),
                "title": jana_tajuk(user_input),
                "timestamp": datetime.now(),
                "history": st.session_state.chat_history.copy()
            })
        else:
            st.session_state.logs[-1]["history"] = st.session_state.chat_history.copy()

        if "rerun_triggered" not in st.session_state or not st.session_state.rerun_triggered:
            st.session_state.rerun_triggered = True
            st.rerun()
