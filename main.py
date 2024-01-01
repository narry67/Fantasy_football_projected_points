from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import numpy as np
import math
from bs4 import BeautifulSoup
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 2000)
def scrape_player_data(player_name, position, team):
    # Set up the web driver (make sure to have the appropriate driver installed, e.g., chromedriver)
    driver = webdriver.Chrome()

    # Navigate to the website
    driver.get("https://www.scoresandodds.com/prop-bets/16563/deandre-hopkins")

    # Find the search input element using XPath
    search_input = driver.find_element("xpath", "/html/body/section[2]/div/header/div/input")

    # Send the value to the search input
    search_input.send_keys(player_name)
    time.sleep(1)
    search_input.send_keys(Keys.RETURN)
    time.sleep(1)

    # Find the desired <a> element using XPath
    target_element = driver.find_element("xpath", "/html/body/section[2]/div/header/div/div/ul/li/a")

    # Get the 'href' attribute from the <a> element
    href_attribute = target_element.get_attribute("href")

    # Print the 'href' attribute
    print(f"Player: {player_name}, Href attribute: {href_attribute}")

    # Navigate to the URL found in href_attribute
    driver.get(href_attribute)

    # Wait for a while to see the changes (optional)
    #driver.implicitly_wait(1)

    # Select the element at /html/body/section[2]/div/div[1]/div[1]/table/tbody
    selected_element = driver.find_element("xpath", "/html/body/section[2]/div/div[1]/div[1]/table/tbody")

    # Extract text content from the selected element
    element_text = selected_element.text

    # Create a dictionary to store the results
    over_under_dict = {"Receiving Yards": {"Line": "na", "Over": "na", "Under": "na"},
                       "Receptions": {"Line": "na", "Over": "na", "Under": "na"},
                       "Touchdowns": {"Line": "na", "Over": "na", "Under": "na"},
                       "Passing Yards": {"Line": "na", "Over": "na", "Under": "na"},
                       "Rushing Yards": {"Line": "na", "Over": "na", "Under": "na"},
                       "Touchdowns": {"Line": "na", "Over": "na", "Under": "na"},
                       "Passing Tds": {"Line": "na", "Over": "na", "Under": "na"},
                       "Completions": {"Line": "na", "Over": "na", "Under": "na"},
                       "Interceptions": {"Line": "na", "Over": "na", "Under": "na"}
                       }
    '''
    # Add keys based on the player's position
    if position == "QB":
        over_under_dict.update({
            "Passing Yards": {"Line": "na", "Over": "na", "Under": "na"},
            "Rushing Yards": {"Line": "na", "Over": "na", "Under": "na"},
            "Touchdowns": {"Line": "na", "Over": "na", "Under": "na"},
            "Passing Tds": {"Line": "na", "Over": "na", "Under": "na"},
            "Completions": {"Line": "na", "Over": "na", "Under": "na"},
            "Interceptions": {"Line": "na", "Over": "na", "Under": "na"}
        })
    '''
    # Extract information based on the available keys
    keys_to_search = list(over_under_dict.keys())

    for key in keys_to_search:
        if key in element_text:
            key_index = element_text.find(key)
            values = element_text[key_index + len(key):].split()[:3]  # Extract the first three numbers
            over_under_dict[key]["Line"] = values[0]
            over_under_dict[key]["Over"] = values[1] if len(values) > 1 else "na"
            over_under_dict[key]["Under"] = values[2] if len(values) > 2 else "na"
        else:
            # Key not found, set values to "na"
            over_under_dict[key]["Line"] = "na"
            over_under_dict[key]["Over"] = "na"
            over_under_dict[key]["Under"] = "na"
    over_under_dict["Position"] = position
    # Print the result dictionary
    print("\nCombined Over/Under Dictionary:")
    print(over_under_dict)

    # Store the results in the team dictionary
    team[player_name] = over_under_dict

    # Close the browser window
    driver.quit()


# Example usage
team = {}
scrape_player_data("jahmyr gibbs", "RB", team)
scrape_player_data("antonio gibson", "RB", team)
scrape_player_data("justin jefferson", "WR", team)
scrape_player_data("deandre hopkins", "WR", team)
scrape_player_data("darren waller", "TE", team)
scrape_player_data("Jalen Hurts", "QB", team)
scrape_player_data("Drake London", "WR", team)
scrape_player_data("Zay Jones", "WR", team)
scrape_player_data("Kareem Hunt", "RB", team)
scrape_player_data("Zach Charbonnet", "RB", team)


# Print the final team dictionary
print("\nFinal Team Dictionary:")
print(team)

# Create an empty list to store rows
rows = []

# Iterate through each player and their stats
for player, stats in team.items():
    for bet_type, values in stats.items():
        if bet_type != 'Position':
            row = {'Player': player, 'Position': stats['Position'], 'Bet Type': bet_type}
            row.update(values)
            rows.append(row)

# Create a DataFrame from the list of rows
df = pd.DataFrame(rows)

# Map the multiplication factors based on the Bet Type
multiplication_factors = {
    'Passing Tds': 4,
    'Touchdowns': 6,
    'Receptions': 1,
    'Interceptions': -2,
    'Completions': 0,
    "Passing Yards": .05
}

# Create a new column 'Projected Points' and handle 'na' values
df['Projected Points'] = df.apply(lambda row: float(row['Line']) * multiplication_factors.get(row['Bet Type'], 0.1) if row['Line'] != 'na' else 0, axis=1)
# Drop rows with 'na' values in the DataFrame
df = df[df['Line'] != 'na']
df = df[df['Over'] != 'na']
df = df[df['Under'] != 'na']
# Display the updated DataFrame
print("Original DataFrame:")
print(df)
# Create a second DataFrame by grouping and summing 'Projected Points'
df_sum = df.groupby('Player')['Projected Points'].sum().reset_index()
# Display the second DataFrame
print("\nDataFrame with Summed Projected Points:")
print(df_sum)