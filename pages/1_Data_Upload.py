import streamlit as st
import pandas as pd

st.title("Data Upload")

st.write("Upload a CSV file, preview the table, apply a simple filter, and download the result.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.write("File uploaded successfully!")
    st.write("Original table:")
    st.dataframe(df.head())

    threshold = st.number_input("Choose a minimum value", value=0.1)

    if st.button("Apply filter"):
        numeric_cols = df.select_dtypes(include="number").columns
        filtered_df = df.copy()

        for col in numeric_cols:
            filtered_df = filtered_df[filtered_df[col] >= threshold]

        st.write("Filtered table:")
        st.dataframe(filtered_df.head())

        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download filtered table",
            data=csv,
            file_name="filtered_table.csv",
            mime="text/csv"
        )
