from HelperFunctions import ListData
import sqlite3

class SteamLeakData(ListData):
    def __init__(self, db_path='SteamLeakDatabase.db'):
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT "LeakID", "LeakNumber", "Status", "Area", "Unit", 
                "Location", "SteamPressureDesign", "SteamPressurePricing",
                "Size", "LossPerYear", "SteamWaste", "Comments",
                "Scaffold", "Insulation", "Isolation", "Turnaround",
                "Notification", "Safety", "DateCompleted", "FuelWaste",
                "CO2", "CH4", "N2O"  -- Ensure N2O is selected here
            FROM leaks
        ''')

        # Fetch all rows from the query
        products = cursor.fetchall()

        # Round the required columns
        rounded_products = []
        for row in products:
            rounded_row = list(row)  # Convert tuple to list for easy modification

            # Indices of the columns that need rounding
            indices_to_round = [9, 19, 20, 21, 22]  # Corresponding to "LossPerYear", "FuelWaste", "CO2", "CH4", "N2O"

            for index in indices_to_round:
                # Handle possible None values to avoid errors
                if rounded_row[index] is not None:
                    rounded_row[index] = round(float(rounded_row[index]), 5)

            rounded_products.append(tuple(rounded_row))  # Convert back to tuple

        # Debug: Print the rounded data to verify N2O inclusion
        print("Rounded data including N2O:")
        for row in rounded_products:
            print(row)

        # Close the connection
        conn.close()

        # Define column count and names, including N2O
        column_count = 23  # Updated to include all 23 columns
        column_names = [
            'Leak ID', 'Leak Identifier', 'Status', 'Area', 'Unit', 'Location', 
            'Steam Pressure Design', 'Steam Pressure Pricing', 'Size', 
            'Loss/Yr', 'Steam Waste', 'Comments', 'Scaffold', 
            'Insulation', 'Isolation', 'Turnaround', 'Notification', 
            'Safety', 'Date Completed', 'Fuel Waste', 'CO2', 'CH4', 'N2O'  # Ensure N2O is listed here
        ]

        # Initialize the parent class with the rounded data
        super().__init__(column_count, column_names, rounded_products)


