def find_value(table, *keys):
    for key in keys:
        if isinstance(table, dict):
            # Attempt to find the key directly
            if key in table:
                table = table[key]
            else:
                # If the key is not found, check for comma-separated keys
                found = False
                for k in table.keys():
                    if key in k.split(', '):
                        table = table[k]
                        found = True
                        break
                if not found:
                    raise KeyError(f"Key '{key}' not found in the table.")
        else:
            raise ValueError("Reached a non-dictionary structure in the table.")
    return table

# Function to check Value
def check_value(val, allowableVal):
    if allowableVal is None:
        return "Value limit not found"
    
    val = int(val)
    allowableVal = int(allowableVal)
    
    if val <= allowableVal:
        return "Passed"
    else:
        return "Failed"
    
from SPARQLWrapper import SPARQLWrapper, JSON

def get_building_info(endpoint_url):
    """
    Fetch construction type, occupancy group, sprinkler type, and storey number from a SPARQL endpoint.
    
    Parameters:
        endpoint_url (str): The URL of the SPARQL endpoint.
        query_file_path (str): The file path to the SPARQL query.
    
    Returns:
        tuple: A tuple containing main_construction_type, subtype, occupancy_group, sprinkler_system, and storey_num.
    """

    # Set up the SPARQL endpoint
    sparql = SPARQLWrapper(endpoint_url)
    
    # Read the SPARQL query from the file
    with open("..\..\..\SPARQL\storeyRule.sparql", "r") as file:
        sparql_query = file.read()

    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Process the results
    for result in results["results"]["bindings"]:
        construction_type = result["constructionType"]["value"]
        occupancy_group = result["occupancyGroup"]["value"]
        sprinkler_type = result["sprinklerType"]["value"] if "sprinklerType" in result else "none"
        storey_num = result["storeyNumValue"]["value"]

        # Splitting the construction type and subtype
        if "-" in construction_type:
            main_construction_type, subtype = construction_type.rsplit("-", 1)
        else:
            main_construction_type = construction_type
            subtype = ""

        # Determine the sprinkler system type
        sprinkler_system = "S" if sprinkler_type != "none" else "NS"

        return main_construction_type, subtype, occupancy_group, sprinkler_system, sprinkler_type, storey_num

import pandas as pd
from IPython.display import display, HTML

def create_scrollable_table(table_data, limit_column_name="Limit", max_height=300):
    """
    Create a scrollable DataFrame from nested table data and display it in a Jupyter Notebook.

    Parameters:
        table_data (dict): Nested dictionary containing the table data to be displayed.
        limit_column_name (str): The name of the column representing the limit value (e.g., "Height Limit" or "Area Limit").
        max_height (int): Maximum height of the scrollable table in pixels. Default is 300.
    
    Returns:
        pd.DataFrame: The DataFrame created from the table data.
    """
    rows = []

    # Process the nested dictionary to create rows for the DataFrame
    for occupancy_group, systems in table_data.items():
        for sprinkler_system, types in systems.items():
            for construction_type, subtypes in types.items():
                for subtype, limit_value in subtypes.items():
                    rows.append({
                        "Occupancy Group": occupancy_group,
                        "Sprinkler System": sprinkler_system,
                        "Construction Type": construction_type,
                        "Subtype": subtype,
                        limit_column_name: limit_value
                    })

    # Create a DataFrame from the rows
    df = pd.DataFrame(rows)

    # Display the DataFrame as a scrollable table
    display(HTML(f"""
    <div style="max-height: {max_height}px; overflow-y: scroll;">
        {df.to_html(index=False)}
    </div>
    """))

    return df
