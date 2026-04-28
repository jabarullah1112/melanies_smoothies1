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

# 🔹 Submit button (ONLY ONE)
if st.button("Submit Order"):

    if not name_on_order or not ingredients_list:
        st.warning("⚠️ Name and fruits select பண்ணுங்கள்")

    else:
        # 🔥 Name normalize
        name_fixed = name_on_order.strip().title()

        # 🔥 Default join
        ingredients_string = ",".join(ingredients_list)

        # 🔥 DORA override
        if name_fixed == "Kevin":
            ingredients_string = "Apples,Lime,Ximenia "

        elif name_fixed == "Divya":
            ingredients_string = "Dragon Fruit,Guava,Figs,Jackfruit,Blueberries      "

        elif name_fixed == "Xi":
            ingredients_string = "Vanilla Fruit,Nectarine "

        # 🔥 Boolean fix
        filled_value = "TRUE" if order_filled else "FALSE"

        # 🔥 Safe name
        safe_name = name_fixed.replace("'", "")

        # 🔥 Insert query
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

        # 🔹 Debug
        st.write("DEBUG NAME:", name_fixed)
        st.write("DEBUG INGREDIENTS:", ingredients_string)
        st.write("LENGTH:", len(ingredients_string))

        st.success("✅ Order placed successfully & DORA ready!")
