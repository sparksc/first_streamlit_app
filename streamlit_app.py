import streamlit
import pandas as pd
import requests
import snowflake.connector
from urllib.error import URLError


def get_fruityvice_data(this_fruit_choice):
  fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{this_fruit_choice}")
  fruityvice_normalized = pd.json_normalize(fruityvice_response.json())
  return fruityvice_normalized


def get_fruit_load_list(sf_cnxn):
  with sf_cnxn.cursor() as my_cur:
    my_cur.execute("SELECT * FROM fruit_load_list")
    return my_cur.fetchall()


# Import Data
my_fruit_list = pd.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')

# Create Menu
streamlit.title('My Parents New Healthy Diner')

streamlit.header('Breakfast Favorites')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')

streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

# Let's put a pick list here so they can pick the fruit they want to include 
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index), ['Avocado', 'Strawberries'])
fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page.
streamlit.dataframe(fruits_to_show)

streamlit.header('Fruityvice Fruit Advice!')

try:
  # Get Fruityvice API Data
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error("Please select a fruit to get information.")
  else:
    # streamlit.write('The user entered', fruit_choice)
    back_from_function = get_fruityvice_data(fruit_choice)
    streamlit.dataframe(back_from_function)
    #streamlit.text(fruityvice_response.json())  # display the raw JSON response

except URLError as e:
  streamlit.error()

# Allow the end user to add a fruit to the list
add_my_fruit = streamlit.text_input('What fruit would you like to add?', 'jackfruit').lower() # Lower user input for API
streamlit.write('Thanks for adding', add_my_fruit)

# Query Snowflake To Get Fruit List
my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])

streamlit.header("The fruit load list contains:")
my_data_rows = get_fruit_load_list(my_cnx)
streamlit.dataframe(my_data_rows)

## Don't run anything past here ##
streamlit.stop()

# Insert user's entry into Snowflake Table
my_cur.execute("INSERT INTO fruit_load_list VALUES ('from streamlit')")

