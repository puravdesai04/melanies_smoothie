# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    "Choose the fruits you want in your custom Smoothie!"
)

# Name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Get Snowflake session
session = get_active_session()

# Get fruit options from Snowflake table
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(col("FRUIT_NAME"))

# Keep dataframe hidden
# st.dataframe(data=my_dataframe, use_container_width=True)

# Choose ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,max_selections=5
)

# Convert list to string and prepare SQL
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Create INSERT statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # Submit button
    time_to_insert = st.button("Submit Order")

    # Insert order into Snowflake
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(
    "Your Smoothie is ordered, " + name_on_order + "!",
    icon="✅"
)