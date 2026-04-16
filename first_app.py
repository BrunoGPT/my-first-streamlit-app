import streamlit as st

st.title("My first Streamlit app")

st.write("""
Welcome to this small test app.

This is a simple prototype created to learn how Streamlit works.
The idea is to build, step by step, a future application for analytical data processing.

Use the page menu on the left to move to the data upload page.
There, you can upload a CSV table, preview the data, apply a simple filter, and download the filtered result.
""")

st.subheader("What this app currently does")

st.write("""
- shows a homepage
- explains the purpose of the app
- provides a second page for table upload
- applies a very simple numeric filter
- allows downloading the filtered table
""")

st.info("This is only a learning prototype. The current filtering step is just a simple example.")