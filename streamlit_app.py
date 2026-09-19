# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col
from cryptography.hazmat.primitives import serialization

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    "Choose the fruits you want in your custom Smoothie!"
)

# Name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")

st.write(
    "The name on your Smoothie will be:",
    name_on_order
)

# Load private key from Streamlit Secrets
private_key = serialization.load_pem_private_key(
    st.secrets["snowflake_private_key"].encode(),
    password=None
)

# Convert private key to DER format
private_key_der = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Get Snowflake session using key-pair authentication
cnx = st.connection(
    "snowflake",
    authenticator="SNOWFLAKE_JWT",
    private_key=private_key_der
)

session = cnx.session()

# Get fruit options from Snowflake table
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Choose ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# Convert list to string and get nutrition information
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        # Get the API search value for the selected fruit
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Optional debugging message from the lesson
        # st.write(
        #     "The search value for ",
        #     fruit_chosen,
        #     " is ",
        #     search_on,
        #     "."
        # )

        st.subheader(
            fruit_chosen + " Nutrition Information"
        )

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Create INSERT statement
    my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # Submit button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered, " + name_on_order + "!",
            icon="✅"
        )
