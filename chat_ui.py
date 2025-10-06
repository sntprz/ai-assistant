# streamlit_app.py
import streamlit as st
import httpx
API_URL = "http://localhost:8000"

st.title("RAG Assistant (MVP)")
q = st.text_input("Your question")
if st.button("Ask") and q:
    with st.spinner("Asking..."):
        resp = httpx.post(f"{API_URL}/query", json={"query": q})
        data = resp.json()
        st.subheader("Answer")
        st.write(data["answer"])
        st.subheader("Sources")
