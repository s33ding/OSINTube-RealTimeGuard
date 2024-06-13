import pandas as pd
import streamlit as st
from  shared_func.main_func import * 
import config
from shared_func.s3_objects import *

# Set the title of the app
st.title("OSINTube")


# Display the image
image_path = config.img_path
st.image(image_path, caption="OSINTube-RealTimeGuard: Real-time Threat Detection for YouTube Content", use_column_width=True)

st.write(config.readme)

# Create a text input widget
st.write(f"try: 'Raça Rubro-Negra Força Jovem'")
input_data = st.text_input("Enter something: ")

# Display the input value when the user presses the enter key
if input_data:
    st.write(f"You entered: {input_data}")
    df = extract_data(input_data)
    key_word = normalize_key_name(input_data)

    upload_dataframe_to_s3(
            dataframe=df, 
            bucket_name=config.bucket_name, 
            key_name=f"dataset/{key_word}/{config.default_file_name}", 
            path=config.output_path, 
            delete=config.delete_file)

    st.write(df)
   

