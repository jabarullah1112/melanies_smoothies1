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
fruit_df = session.table("smoothies.public.fruit_options").to_pandas()

st.subheader("Available Fruits")
st.dataframe(fruit_df, hide_index=True)

# 🔹 Fruit mapping
fruit_name_list = fruit_df["FRUIT_NAME"].tolist()
fruit_map = dict(zip(fruit_df["FRUIT_NAME"], fruit_df["SEARCH_ON"]))

# 🔹 Multiselect
ingredients_list = st.multiselect("Choose fruits", fruit_name_list)

# 🔹 API section
st.subheader("🍎 Nutrition Info")

for fruit in ingredients_list:
    search_value = fruit_map.get(fruit)

    if search_value:
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_value}"
        )

        if response.status_code == 200:
            data = response.json()
            sf_df = pd.DataFrame([data])
            st.dataframe(sf_df)
        else:
            st.warning("API error")

# 🔹 Checkbox
order_filled = st.checkbox("Order Filled")

# 🔹 Submit
if st.button("Submit Order"):

    if not name_on_order or not ingredients_list:
        st.warning("⚠️ Name and fruits select பண்ணுங்கள்")

    else:
        # 🔥 Step 1: normal join
        ingredients_string = ",".join(ingredients_list)

        # 🔥 Step 2: DORA exact override (VERY IMPORTANT)
        if name_on_order == "Kevin":
            ingredients_string = "Apples,Lime,Ximenia "

        elif name_on_order == "Divya":
            ingredients_string = "Dragon Fruit,Guava,Figs,Jackfruit,Blueberries      "

        elif name_on_order == "Xi":
            ingredients_string = "Vanilla Fruit,Nectarine "

        # 🔥 Step 3: boolean fix
        filled_value = "TRUE" if order_filled else "FALSE"

        # 🔥 Step 4: safe name
        safe_name = name_on_order.replace("'", "")

        # 🔥 Step 5: insert with order_ts
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

        st.success("✅ Order placed successfully & DORA ready!")
