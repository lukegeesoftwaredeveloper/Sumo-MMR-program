import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


# Define a function to find the past odd-numbered months and their years
def find_past_odd_months(current_date, num_months):
    # Get the current month and year
    current_month = current_date.month
    current_year = current_date.year

    # Initialize lists to store the past odd-numbered months and their years
    past_odd_months = []
    past_years = []

    while num_months > 0:
        # Calculate the month to check, starting from the current month
        current_month -= 1
    # We check if current_month has gone below 1 (which corresponds to January).
        # If it has, we decrement the current_year by 1 to move to the previous year,
        # and we set current_month to 12 to wrap around to December.
        if current_month <= 0:
            # If the month goes past January, adjust the year and month
            current_year -= 1
            current_month = 12

        # Check if the current month is odd. only even numbers don't have a remainder when divided by 2
        # and only if it is odd since sumo tournaments are held on odd months do we get the past 5 banzuke
        if current_month % 2 != 0:
            # Create a new datetime with the adjusted year and month
            adjusted_date = datetime(current_year, current_month, 1)
            past_odd_months.append(adjusted_date)
            past_years.append(current_year)
            num_months -= 1

    return past_odd_months, past_years


# Make a function that does the math on a rikishi's scores we'll possibly make this more complex as we go on
def calculate_scores(values):
    total_wins = 0
    total_losses = 0
    total_absents = 0
    health = None  # Initialize health as None

    for value in values:
        # Use regular expression to find all numbers in the string c+ bc we need them when they are double digits
        numbers = re.findall(r'\d+', value)

        if numbers:
            # Extract the numbers as integers
            if len(numbers) == 2:
                wins = int(numbers[0])
                losses = int(numbers[1])
                absents = 0
            elif len(numbers) == 3:
                wins = int(numbers[0])
                losses = int(numbers[1])
                absents = int(numbers[2])
            else:
                continue  # Skip invalid formats

            total_wins += wins
            total_losses += losses
            if absents != 15:
                total_absents += absents
            # Check if the first entry is "0-0-15" and update health
            if values.index(value) == 0 and value == "0-0-15":
                health = "healing"

    total_losses += total_absents  # Add absents to losses

    return total_wins, total_losses, health


# Get the current date
current_date = datetime.now()

# Find the past 5 odd-numbered months and their years
past_odd_months, past_years = find_past_odd_months(current_date, 5)

# Define the base URL for sumo data
base_url = "http://sumodb.sumogames.de/Banzuke.aspx"

# instantiate the rikishi dictionary
rikishi = {}

# instantiate a rikishi array for just names
rikishi_array = []
# This if not statement will keep a programmer employed since it has to be manually updated everytime the Japanese Sumo
# Association announces when they are going to release a banzuke and when tournaments start and end. Luckily for us they
# have the next 2 years planned out, but their website doesn't allow web scraping, so we are using a long if not or
# statement because to me it makes more sense/ is easier
if not ((datetime(2023, 9, 24) <= current_date <= datetime(2023, 10, 29)) or (datetime(2023, 11, 27) <= current_date <= datetime(2023, 12, 24)) or (datetime(2024, 1, 28) <= current_date <= datetime(2024, 2, 25)) or (datetime(2024, 3, 24) <= current_date <= datetime(2024, 4, 29)) or (datetime(2024, 5, 26) <= current_date <= datetime(2024, 6, 30)) or (datetime(2024, 7, 28) <= current_date <= datetime(2024, 8, 25)) or (datetime(2024, 9, 22) <= current_date <= datetime(2024, 10, 27)) or (datetime(2024, 11, 25) <= current_date <= datetime(2024, 12, 23))):
    # First we need to grab the current banzuke but JUST the names
    # to eventually check if those names are in our rikishi dictionary we'll eventually put this
    # into a loop that makes sure
    # there is a current banzuke to check based on certain dates
    this_year = current_date.year
    this_month = current_date.month
    new_banzuke_url = f"{base_url}?b={this_year}{this_month:02d}&heya=-1&shusshin=-1"
    # Send an HTTP GET request to the URL
    response = requests.get(new_banzuke_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the table with class "banzuke"
        banzuke_table = soup.find("table", {"class": "banzuke"})

        if banzuke_table:
            # Iterate through all rows (rikishi) in the table body
            for row in banzuke_table.find("tbody").find_all("tr"):
                # Check if the row has the class "emptycell," and skip it if it does

                # Find the relevant data within the row
                columns = row.find_all("td")

                # Ensure that there are at least 2 columns (name and score)
                if len(columns) >= 2 and "emptycell" not in columns[0].get("class", []):
                    rikishi_name = columns[1].find("a").text.strip() if columns[1].find("a") else ""
                    # Grabbing the names off the current banzuke and adding them to our list/array
                    rikishi_array.append(rikishi_name)

                elif "emptycell" in columns[0].get("class", []):
                    rikishi_name = columns[2].find("a").text.strip() if columns[2].find("a") else ""
                    rikishi_array.append(rikishi_name)

                if len(columns) >= 5:
                    rikishi_name2 = columns[3].find("a").text.strip() if columns[3].find("a") else ""
                    rikishi_array.append(rikishi_name2)

        else:
            print("Could not find the banzuke table.")

    else:
        print("Failed to retrieve the webpage. The banzuke isn't out yet. Status code:", response.status_code)

    # Iterate through each past odd-numbered month
    for i in range(len(past_odd_months)):
        year = past_years[i]
        month = past_odd_months[i].month
        # Construct the URL for the current past month
        url = f"{base_url}?b={year}{month:02d}&heya=-1&shusshin=-1"

        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")
            print("Banzuke")
            print("-------------")

            # Locate all tables with class "banzuke"
            banzuke_tables = soup.find_all("table", {"class": "banzuke"},)
            # Iterate through the tables and check their captions
            for table in banzuke_tables:
                # Find the first caption element
                caption = table.find("caption")

                if caption and ("Makuuchi Banzuke" in caption.get_text() or "Juryo Banzuke" in caption.get_text()):
                    # Iterate through all rows (rikishi) in the table body
                    for row in table.find("tbody").find_all("tr"):
                        # Check if the row has the class "emptycell," and skip it if it does

                        # Find the relevant data within the row
                        columns = row.find_all("td")

                        # Ensure that there are at least 2 columns (name and score) some rows have a collumn
                        # with an emptycell
                        # filling up a row spot. So we want to make sure the ones that start with that
                        # go to the next loop and
                        # instead check the specific indexes that the rikishi name and score are at in those scenarios

                        if len(columns) >= 2 and "emptycell" not in columns[0].get("class", []):
                            rikishi_name = columns[1].find("a").text.strip() if columns[1].find("a") else ""
                            rikishi_score = columns[0].text.strip()
                            # Here, we check if the rikishi_name (the name of the sumo wrestler) is already a key in a
                            # dictionary we made named rikishi.
                            if rikishi_name in rikishi:
                                rikishi[rikishi_name].append(rikishi_score)
                            else:
                                # In this case, we create a new entry in the rikishi dictionary with
                                # rikishi_name as the key,
                                # and the value is a new list containing just the rikishi_score.
                                # This initializes a new entry
                                # for a wrestler who hasn't been encountered before in the data.
                                rikishi[rikishi_name] = [rikishi_score]
                        elif "emptycell" in columns[0].get("class", []):
                            rikishi_name = columns[2].find("a").text.strip() if columns[2].find("a") else ""
                            rikishi_score = columns[3].text.strip()
                            if rikishi_name in rikishi:
                                rikishi[rikishi_name].append(rikishi_score)
                            else:
                                rikishi[rikishi_name] = [rikishi_score]

                        if len(columns) >=5:
                            rikishi_name2 = columns[3].find("a").text.strip() if columns[3].find("a") else ""
                            rikishi_score2 = columns[4].text.strip()
                            if rikishi_name2 in rikishi:
                                rikishi[rikishi_name2].append(rikishi_score2)
                            else:
                                rikishi[rikishi_name2] = [rikishi_score2]
                else:
                    continue

        else:
            print("Failed to retrieve the webpage. Status code:", response.status_code)

    # Print the rikishi dictionary (debug option)
    #for name, scores in rikishi.items():
    #    print(f"Rikishi: {name}, Scores: {', '.join(scores)}")
    # This rikishi changed his name after being promoted to ozeki and thus needed his dict socres to be updated
    if 'Kirishima' in rikishi and 'Kiribayama' in rikishi:
        # Merge Kirishima's scores with Kiribayama's scores
        rikishi['Kirishima'].extend(rikishi['Kiribayama'])

    # Create a dictionary to store rikishi data
    rikishi_data = {}
    for current_rikishi in rikishi_array:
        if current_rikishi in rikishi:
            scores_for_current = rikishi[current_rikishi]
            # Calculate the win-loss totals
            total_wins, total_losses, health = calculate_scores(scores_for_current)
            # (debug print) print(current_rikishi +"'s number would be: " + str(total_wins -total_losses))
            overall_score = total_wins-total_losses
            if health == "healing":
                user_input = input("Is " + current_rikishi + " attending this tournament? Y/N: ")
                if user_input.lower() == 'y':
                    # Store rikishi data with their overall score and attendance status
                    rikishi_data[current_rikishi] = (overall_score, True)
                elif user_input.lower() == 'n':
                    # Store rikishi data with their overall score and attendance status
                    rikishi_data[current_rikishi] = (overall_score, False)
                else:
                    print("Invalid input. Please enter 'Y' or 'N'.")
            else:
                # Store rikishi data with their overall score and attendance status as False
                rikishi_data[current_rikishi] = (overall_score, False)

    # Sort rikishi_data by overall scores in descending order
    sorted_rikishi = sorted(rikishi_data.items(), key=lambda x: x[1][0], reverse=True)

    # Initialize the user's excluded choices
    excluded_choices = []

    while len(excluded_choices) < len(current_rikishi):
        # Filter out already excluded choices
        available_rikishi = [rikishi[0] for rikishi in sorted_rikishi if rikishi[0] not in excluded_choices]

        if not available_rikishi:
            print("No more rikishi available.")
            break

        print("Top 3 Rikishi:")
        for i, rikishi_name in enumerate(available_rikishi[:3]):
            print(f"{i + 1}. {rikishi_name}")

        user_input = input("You can pick 1 Ozeki, 1 Sekiwake OR Komusubi and 1 Maegashira. "
                           "Choose a rikishi to exclude until they meet this criteria. (1/2/3), or '0' to continue: ")

        if user_input == '0':
            break
        elif user_input.isdigit() and 1 <= int(user_input) <= len(available_rikishi):
            excluded_rikishi = available_rikishi[int(user_input) - 1]
            excluded_choices.append(excluded_rikishi)
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 0 to continue.")

    # Update the top 3 rikishi after all exclusions
    top_3_rikishi = [rikishi[0] for rikishi in sorted_rikishi if rikishi[0] not in excluded_choices][:3]
    # Now 'excluded_choices' contains the rikishi names the user excluded,
    # and 'top_3_rikishi' contains the remaining top 3 choices.
else:
    print("The next banzuke isn't out yet! :)")
