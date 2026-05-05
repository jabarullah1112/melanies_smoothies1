import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark import Session

# 🔹 Snowflake connection
connection_parameters = st.secrets["snowflake"]
session = Session.builder.configs(connection_parameters).create()

# 🔹 Title
st.title("🍹 Smoothie Order App")

# 🔹 Name input
name_on_order = st.text_input("Enter your name")

# 🔹 Load fruits
pd_df = session.table("smoothies.public.fruit_options").to_pandas()

st.subheader("Available Fruits")
st.dataframe(pd_df, hide_index=True)

# 🔹 Fruit list
fruit_name_list = pd_df["FRUIT_NAME"].tolist()

# 🔹 Multiselect
ingredients_list = st.multiselect("Choose fruits", fruit_name_list)

# 🔹 API section
st.subheader("🍎 Nutrition Info")

for fruit_chosen in ingredients_list:
    search_on = pd_df.loc[
        pd_df['FRUIT_NAME'] == fruit_chosen,
        'SEARCH_ON'
    ].iloc[0]

    response = requests.get(
        f"https://my.smoothiefroot.com/api/fruit/{search_on}"
    )

    if response.status_code == 200:
        data = response.json()
        st.dataframe(pd.DataFrame([data]))
    else:
        st.warning("API error")

# 🔹 Checkbox
order_filled = st.checkbox("Order Filled")

# 🔹 Submit
if st.button("Submit Order"):

    if not name_on_order or not ingredients_list:
        st.warning("⚠️ Name and fruits select பண்ணுங்கள்")

    else:
        name_fixed = name_on_order.strip().title()
        ingredients_string = ",".join(ingredients_list)

        filled_value = "TRUE" if order_filled else "FALSE"
        safe_name = name_fixed.replace("'", "")

        query = f"""
        INSERT INTO smoothies.public.orders
        (name_on_order, ingredients, order_filled, order_ts)
        VALUES (
            '{safe_name}',
            '{ingredients_string}',
            {filled_value},
            CURRENT_TIMESTAMP()
        )
        """

        session.sql(query).collect()

        st.success("✅ Order placed successfully!")
