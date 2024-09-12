import re
import logging
import math

def process_input(input_text: str) -> str:
    # Regex patterns for detecting building type, occupants, dwelling units, peak visitors, and area
    building_type_pattern = r"(commercial|institutional|residential|retail)"
    occupants_pattern = r"(regular\s+building\s+occupants|residents|people)\s*=\s*(\d+)"
    dwelling_units_pattern = r"number\s*of\s*dwelling\s*units\s*=\s*(\d+)"
    peak_visitors_pattern = r"peak\svisitors\s*=\s*([\d.]+)"
    peak_inpatients_pattern = r"peak\sinpatients\s*=\s*([\d.]+)"
    qualifying_outpatients_pattern = r"qualifying\soutpatients\s*=\s*([\d.]+)"
    baseline_energy_pattern = r"(?i)\b(?:baseline\s+(?:annual\s+)?energy)\s*=\s*([\d.]+)"
    proposed_energy_pattern = r"(?i)\b(?:proposed\s+(?:annual\s+)?energy)\s*=\s*([\d.]+)"

    # Area patterns with unit specifications
    unit_pattern = r"(foot|ft|feet|foot2|ft2|feet2|m|meter|meter2|m2)"
    
    # Area patterns with unit specifications
    area_pattern = r"(\s*floor\s*area|floor\s*area|building\s*area|area)\s*=\s*([\d.]+)\s*(foot|ft|foot\^2|ft\^2|meter|m|meter\^2|m\^2)"
    
    # Length and width patterns with unit specifications
    length_width_pattern = (
        r"(?:length\s*=\s*(?P<length>[\d.]+)\s*(?P<length_unit>foot|ft|meter|m)\s*(?:,|and)?\s*width\s*=\s*(?P<width>[\d.]+)\s*(?P<width_unit>foot|ft|meter|m)|"
        r"width\s*=\s*(?P<width2>[\d.]+)\s*(?P<width_unit2>foot|ft|meter|m)\s*(?:,|and)?\s*length\s*=\s*(?P<length2>[\d.]+)\s*(?P<length_unit2>foot|ft|meter|m))"
    )
    
    # Total parking space pattern
    Total_parking_space_pattern = r"(Total\s*parking\s*space|Total\s*space|Total\s*spaces|Total\s*parking\s*spaces)\s*=\s*(\d+)"

    # Restoration and site area patterns
    restoration_area_pattern = r"Restoration\s*area\s*=\s*([\d.]+)"
    disturbed_area_pattern = r"Total\s*previously\s*disturbed\s*site\s*area\s*=\s*([\d.]+)"
    
    # Total site area and required open space patterns
    Required_open_space_pattern = r"(required\s*open\s*space|open\s*space)\s*=\s*([\d.]+)"
    total_site_area_pattern = r"Total\s*site\s*area\s*=\s*([\d.]+)"

    # patterns for runoff equation
    rainfall_pattern = r"rainfall\s*=\s*([\d.]+)(?:\s*(mm/hr|mm))?"
    depression_storage_pattern = r"depression\s*storage\s*=\s*([\d.]+)(?:\s*(mm/hr|mm))?"
    infiltration_pattern = r"infiltration\s*=\s*([\d.]+)(?:\s*(mm/hr|mm))?"
    # pattern for Previously Developed Land
    previously_area_pattern = r"Area\s*of\s*previously\s*developed\s*land\s*=\s*([\d.]+)"
    development_footprint_pattern = r"development\s*footprint\s*=\s*([\d.]+)"
    
    #patterns for long and short-term and area for bicycle racks,and for R-value
    long_term_pattern = r"long\s*term\s*=\s*([\d]+)"
    short_term_pattern = r"short\s*term\s*=\s*([\d]+)"
    area_racks_pattern = r"(area|floor|building)\s*=\s*([\d.]+)"
    material_thickness_pattern = r"material\s*thickness\s*=\s*([\d.]+)"
    thermal_conductivity_pattern = r"thermal\s*conductivity\s*=\s*([\d.]+)"
   
    # Search for intents in the user input
    long_term_intent = "long-term bicycle storage" in input_text
    short_term_intent = "short-term bicycle storage" in input_text
    shower_facilities_intent = any(phrase in input_text.lower() for phrase in ["shower facilities", "shower", "shower facility"])
    number_Preferred_spaces_intent = any(phrase in input_text.lower() for phrase in ["preferred space", "preferred spaces", "required number of preferred spaces", "required number of preferred space"])
    fueling_stations_intent = any(phrase in input_text.lower() for phrase in ["fueling stations", "fuel stations", "required number of fueling stations", "required number of fuel stations"])
    restoration_area_intent = any(phrase in input_text.lower() for phrase in ["percentage of restoration area", "restoration area percentage"])
    open_space_intent = any(phrase in input_text.lower() for phrase in ["required open space", "open space requirement"])
    vegetated_space_intent = "vegetated space" in input_text
    outdoor_area_intent = any(phrase in input_text.lower() for phrase in ["required outdoor area", "outdoor area requirement", "outdoor space"])
    air_volume_intent_before_occupancy = any (phrase in input_text.lower() for phrase in [ "air volume before occupancy", "flush out before occupancy"])
    air_volume_intent_during_occupancy = any (phrase in input_text.lower() for phrase in [ "air volume during occupancy", "flush out during occupancy"])
    air_volume_intent_to_complete = any (phrase in input_text.lower() for phrase in [ "air volume during occupancy to complete", "flush out to complete"])
     # intent for runoff calculation
    runoff_intent = any(phrase in input_text.lower() for phrase in ["runoff", "Expected runoff","run off"])
    # Intent for % of development on previously developed land
    development_percentage_intent = any(phrase in input_text.lower() for phrase in ["previously developed land", "percentage of previously developed land"])
    Bicycle_racks_intent = any(phrase in input_text.lower() for phrase in ["Number of bicycle racks required","total of bicycle racks","bicycle racks"])
    Energy_performance_intent = any(phrase in input_text.lower() for phrase in["energy performance","energy improvement"])
    R_value_intent = any(phrase in input_text.lower() for phrase  in["r-value", "r value"])
    # Search for building type, number of occupants, dwelling units, peak visitors, and area
    building_type_match = re.search(building_type_pattern, input_text, re.IGNORECASE)
    occupants_match = re.search(occupants_pattern, input_text, re.IGNORECASE)
    dwelling_units_match = re.search(dwelling_units_pattern, input_text, re.IGNORECASE)
    peak_visitors_match = re.search(peak_visitors_pattern, input_text, re.IGNORECASE)
    area_match = re.search(area_pattern, input_text, re.IGNORECASE)
    length_width_match = re.search(length_width_pattern, input_text, re.IGNORECASE)
    Total_parking_match = re.search(Total_parking_space_pattern, input_text, re.IGNORECASE)
    restoration_area_match = re.search(restoration_area_pattern, input_text, re.IGNORECASE)
    disturbed_area_match = re.search(disturbed_area_pattern, input_text, re.IGNORECASE)
    total_site_area_match = re.search(total_site_area_pattern, input_text, re.IGNORECASE)
    required_open_space_match = re.search(Required_open_space_pattern, input_text, re.IGNORECASE)
    qualifying_outpatients_match = re.search(qualifying_outpatients_pattern, input_text, re.IGNORECASE)
    peak_inpatients_match = re.search(peak_inpatients_pattern, input_text, re.IGNORECASE)
    unit_match = re.search(unit_pattern, input_text, re.IGNORECASE)
    rainfall_match = re.search(rainfall_pattern, input_text, re.IGNORECASE)
    depression_storage_match = re.search(depression_storage_pattern, input_text, re.IGNORECASE)
    infiltration_match = re.search(infiltration_pattern, input_text, re.IGNORECASE)
    previously_area_match = re.search(previously_area_pattern,input_text, re.IGNORECASE)
    development_footprint_match = re.search(development_footprint_pattern,input_text, re.IGNORECASE)
    long_term_match = re.search(long_term_pattern,input_text, re.IGNORECASE)
    short_term_match = re.search(short_term_pattern,input_text, re.IGNORECASE)
    area_racks_match = re.search(area_racks_pattern,input_text, re.IGNORECASE)
    baseline_energy_match = re.search(baseline_energy_pattern, input_text, re.IGNORECASE)
    proposed_energy_match = re.search(proposed_energy_pattern, input_text, re.IGNORECASE)
    material_thickness_match = re.search(material_thickness_pattern, input_text, re.IGNORECASE)
    thermal_conductivity_match = re.search(thermal_conductivity_pattern, input_text, re.IGNORECASE)

    # Handle R-value calculation
    if R_value_intent:
        if material_thickness_match and thermal_conductivity_match:
            try:
                # Extract and convert values
                material_thickness = float(material_thickness_match.group(1))
                thermal_conductivity = float(thermal_conductivity_match.group(1))
                 # Calculate R-value
                R_value = math.ceil(material_thickness / thermal_conductivity)
                return f"R-value = {R_value} (m²·K/W)"
            except ValueError:
                logging.error("Value error in R-value calculation.")
                return "Invalid input values for material thickness or thermal conductivity. Please specify correct numbers."
        else:
            return "Invalid input for R-value calculation. Please specify both 'Material Thickness' and 'Thermal Conductivity'."
    
    # Handle long-term bicycle storage calculations
    if long_term_intent:
        if building_type_match:
            building_type = building_type_match.group(1).lower()
            if building_type == 'residential':
                if occupants_match and dwelling_units_match:
                    try:
                        regular_occupants = float(occupants_match.group(2))
                        dwelling_units = float(dwelling_units_match.group(1))
                        occupants_bikes_required = regular_occupants * 0.30
                        bikes_required = max(math.ceil(occupants_bikes_required), math.ceil(dwelling_units))
                        return f"{bikes_required} Bicycles required for long-term storage (residential)"
                    except ValueError:
                        logging.error("Value error in calculation for residential.")
                        return "Invalid input values for occupants or dwelling units. Please specify correct numbers."
                elif occupants_match:
                    try:
                        regular_occupants = float(occupants_match.group(2))
                        bikes_required = math.ceil(regular_occupants * 0.30)
                        return f"{bikes_required} Bicycles storage required for long-term storage (residential)"
                    except ValueError:
                        logging.error("Value error in occupants calculation.")
                        return "Invalid input for regular building occupants. Please specify a correct number."
                elif dwelling_units_match:
                    try:
                        dwelling_units = float(dwelling_units_match.group(1))
                        bikes_required = math.ceil(dwelling_units)
                        return f"{bikes_required} Bicycles storage required for long-term storage (residential)"
                    except ValueError:
                        logging.error("Value error in dwelling units calculation.")
                        return "Invalid input for number of dwelling units. Please specify a correct number."
                else:
                    return "Please specify 'Regular Building occupants' or 'number of dwelling units' for residential buildings."

            elif building_type in ['commercial', 'institutional']:
                if occupants_match:
                    try:
                        regular_occupants = float(occupants_match.group(2))
                        multiplier = 0.05
                        long_term_bikes_required = regular_occupants * multiplier
                        return f"{math.ceil(long_term_bikes_required)} Bicycles required for long-term storage ({building_type})"
                    except ValueError:
                        logging.error("Value error in occupants calculation.")
                        return "Invalid input for regular building occupants. Please specify a correct number."
        return "Invalid input for long-term storage. Please specify 'Regular Building occupants = <number>' or 'dwelling units' with 'Building type'."

    # Handle shower facilities calculation
    if shower_facilities_intent:
        if occupants_match:
            try:
                regular_occupants = float(occupants_match.group(2))
                if regular_occupants <= 100:
                    showers_required = 1
                else:
                    showers_required = math.ceil((1 + (regular_occupants - 100)) / 150)
                return f"{showers_required} Showers required"
            except ValueError:
                logging.error("Value error in shower facilities calculation.")
                return "Invalid input for regular building occupants. Please specify a correct number."
        return "Error: The input does not contain sufficient data for shower facilities calculation."

    # Handle short-term storage calculation
    if short_term_intent:
        if peak_visitors_match:
            try:
                peak_visitors = float(peak_visitors_match.group(1))
                bikes_required = peak_visitors * 0.025
                return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on peak visitors"
            except ValueError:
                logging.error("Value error in peak visitors calculation.")
                return "Invalid input for peak visitors. Please specify a correct number."
    if short_term_intent:
        if area_match:
            try:
                area = float(area_match.group(2))
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    bikes_required = 2 * (area / 5000)
                    return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on area in square feet"
                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    bikes_required = 2 * (area / 465)
                    return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on area in square meters"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in area calculation.")
                return "Invalid input for area. Please specify a correct number."
    if short_term_intent:
        if length_width_match:
            try:
            # Capture length and width irrespective of their order and separator
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')
            
                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    bikes_required = 2 * (area / 5000)
                    return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on length and width in feet"
                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    bikes_required = 2 * (area / 465)
                    return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on length and width in meters"
                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."
            except ValueError:
                logging.error("Value error in length and width calculation.")
                return "Invalid input for length and width. Please specify correct numbers."
    
    # Required number of Preferred spaces
    if number_Preferred_spaces_intent:
        if Total_parking_match:
            try:
                Total_parking_spaces = float(Total_parking_match.group(2))
                Preferred_spaces = Total_parking_spaces * 0.05
                return f"{math.ceil(Preferred_spaces)} parking spaces required"
            except ValueError:
                logging.error("Value error in Total parking spaces")
                return "Invalid input for Total parking spaces."
        else:
            return "Invalid input for Preferred space. Please specify 'Total parking spaces = <number>'."
    
    # Required number of Fueling stations
    if fueling_stations_intent:
        if Total_parking_match:
            try:
                Total_parking_spaces = float(Total_parking_match.group(2))
                Fueling_stations = Total_parking_spaces * 0.02
                return f"{math.ceil(Fueling_stations)} fueling stations required"
            except ValueError:
                logging.error("Value error in Total parking spaces")
                return "Invalid input for Total parking spaces."
        else:
            return "Invalid input for Fueling stations. Please specify 'Total parking spaces = <number>'."
    
    # Percentage of Restoration Area
    if restoration_area_intent:
        if restoration_area_match and disturbed_area_match:
            try:
                restoration_area = float(restoration_area_match.group(1))
                disturbed_area = float(disturbed_area_match.group(1))
                percentage_restoration = math.ceil((restoration_area / disturbed_area) * 100)
                return f"{percentage_restoration:.2f}% restoration area"
            except ValueError:
                logging.error("Value error in restoration area calculation.")
                return "Invalid input for restoration area or total disturbed area."
        else:
            return "Invalid input for restoration area percentage. Please specify both 'Restoration area = <number>' and 'Total previously disturbed site area = <number>'."
     # Vegetated Space
    if vegetated_space_intent:
        # Check if either required_open_space_match or total_site_area_match is valid
        if required_open_space_match:
            try:
                required_open_space = float(required_open_space_match.group(2))
                vegetated_space = math.ceil(required_open_space * 0.25)
                return f"≥ {vegetated_space:.2f}% vegetated space required"
            except ValueError:
                logging.error("Value error in required open space calculation.")
                return "Invalid input for required open space."
        elif total_site_area_match:
            try:
                total_site_area = float(total_site_area_match.group(1))
                required_open_space = math.ceil(total_site_area * 0.30)
                vegetated_space = math.ceil(required_open_space * 0.25)
                return f"≥ {vegetated_space:.2f}% vegetated space required"
            except ValueError:
                logging.error("Value error in total site area calculation.")
                return "Invalid input for total site area."
        else:
            return "Invalid input for vegetated space. Please specify 'Required open space = <number>' or 'Total site area = <number>'."

    # Required Open Space
    if open_space_intent:
        if total_site_area_match:
            try:
                total_site_area = float(total_site_area_match.group(1))
                required_open_space = math.ceil(total_site_area * 0.30)
                return f"≥ {required_open_space:.2f}% open space required"
            except ValueError:
                logging.error("Value error in total site area calculation.")
                return "Invalid input for total site area."
        else:
            return "Invalid input for open space. Please specify 'Total site area = <number>'."
     # Required Outdoor Area Calculation
    if outdoor_area_intent:
        if unit_match and peak_inpatients_match and qualifying_outpatients_match:
            try:
                peak_inpatients = float(peak_inpatients_match.group(1))
                qualifying_outpatients = float(qualifying_outpatients_match.group(1))
                unit1 = unit_match.group(1).lower()
                    
                if unit1 in ['meter', 'm', 'meter^2', 'm^2']:
                    required_outdoor_area = 0.5 * (0.75 * peak_inpatients) + 0.5 * (0.75 * qualifying_outpatients)
                    return f"Required outdoor area: {math.ceil(required_outdoor_area)} m²"
                    
                elif unit1 in ['foot', 'ft', 'foot^2', 'ft^2']:
                    required_outdoor_area = 5 * (0.75 * peak_inpatients) + 5 * (0.75 * qualifying_outpatients)
                    return f"Required outdoor area: {math.ceil(required_outdoor_area):.2f} ft²"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in outdoor area calculation.")
                return "Invalid input for peak inpatients or qualifying outpatients. Please specify correct numbers."
        else:
            return "Invalid input for outdoor area. Please specify 'Area unit', 'Peak inpatients', and 'Qualifying outpatients'."
     # Calculate Air Volume Needed before Occupancy
    if air_volume_intent_before_occupancy:
        if length_width_match:
            try:
                # Calculate area from length and width
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')

                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 14000)  # ft³
                    return f"Air volume needed before occupancy: {air_volume} ft³"
                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 4267140)  # liters
                    return f"Air volume needed before occupancy: {air_volume} l"
                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."
            except ValueError:
                logging.error("Value error in air volume calculation.")
                return "Invalid input for length and width. Please specify correct numbers."
        elif area_match:
            try:
                area = float(area_match.group(2))
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 14000)  # ft³
                    return f"Air volume needed before occupancy: {air_volume} ft³"
                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 4267140)  # liters
                    return f"Air volume needed before occupancy: {air_volume} l"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in area calculation.")
                return "Invalid input for area. Please specify a correct number."
        else:
            return "Invalid input for air volume calculation. Please specify area or length and width."
            
  # Calculate Air Volume Needed during  Occupancy to complete
    if air_volume_intent_to_complete:
        if length_width_match:
            try:
                # Calculate area from length and width
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')

                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 10500)  # ft³
                    return f"Air volume needed during occupancy to complete: {air_volume} ft³"
                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 3200880)  # liters
                    return f"Air volume needed during occupancy to complete: {air_volume} l"
                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."
            except ValueError:
                logging.error("Value error in air volume calculation.")
                return "Invalid input for length and width. Please specify correct numbers."
        elif area_match:
            try:
                area = float(area_match.group(2))
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 10500)  # ft³
                    return f"Air volume needed during occupancy to complete: {air_volume} ft³"
                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 3200880)  # liters
                    return f"Air volume needed during occupancy to complete: {air_volume} l"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in area calculation.")
                return "Invalid input for area. Please specify a correct number."
        else:
            return "Invalid input for air volume calculation. Please specify area with unit or length and width with unit."  
     # Calculate Air Volume Needed during  Occupancy
    if air_volume_intent_during_occupancy:
        if length_width_match:
            try:
                # Calculate area from length and width
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')

                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 3500)  # ft³
                    return f"Air volume needed during occupancy: {air_volume} ft³"
                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 1066260)  # liters
                    return f"Air volume needed during occupancy: {air_volume} l"
                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."
            except ValueError:
                logging.error("Value error in air volume calculation.")
                return "Invalid input for length and width. Please specify correct numbers."
        elif area_match:
            try:
                area = float(area_match.group(2))
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 3500)  # ft³
                    return f"Air volume needed during occupancy: {air_volume} ft³"
                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 1066260)  # liters
                    return f"Air volume needed during occupancy: {air_volume} l"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in area calculation.")
                return "Invalid input for area. Please specify a correct number."
        else:
            return "Invalid input for air volume calculation. Please specify area with unit or length and width with unit."
    # Handle runoff calculation
    if runoff_intent:
        if rainfall_match and depression_storage_match and infiltration_match:
            try:
                rainfall = float(rainfall_match.group(1))
                depression_storage = float(depression_storage_match.group(1))
                infiltration = float(infiltration_match.group(1))
                
                runoff = math.ceil(rainfall - depression_storage - infiltration)
                return f"Runoff = {runoff} mm/hr"
            except ValueError:
                logging.error("Value error in runoff calculation.")
                return "Invalid input values for runoff calculation. Please specify correct numbers for Rainfall, Depression Storage, and Infiltration."
        else:
            return "Missing input for runoff calculation. Please specify 'Rainfall = <number>', 'Depression storage = <number>', and 'Infiltration = <number>'."
    # Handle the % of development on previously developed land
    if development_percentage_intent:
        if previously_area_match and development_footprint_match:
            try:
                previously_developed_land = float(previously_area_match.group(1))
                development_footprint = float(development_footprint_match.group(1))
                
                if development_footprint == 0:
                    return "Area of development footprint cannot be zero."
                
                development_percentage = math.ceil(100 * (previously_developed_land / development_footprint))
                return f"Percentage of development on previously developed land = {development_percentage}%"
            except ValueError:
                logging.error("Value error in development percentage calculation.")
                return "Invalid input values for development percentage. Please specify correct numbers."
        else:
            return "Missing input for development percentage. Please specify 'Area of previously developed land' and 'Area of development footprint'."
    # Condition 1: Long-term or not mentioned (default is long-term)
    if Bicycle_racks_intent:
        if occupants_match:
                try:
                    occupants = float(occupants_match.group(2))  # Get the number of occupants
                    total_racks = math.ceil(occupants / 20)
                    return f"Total number of bicycle racks required (long-term): {total_racks}"
                except ValueError:
                    logging.error("Invalid value for occupants in long-term bicycle storage calculation.")
                    return "Invalid input for building occupants. Please specify a correct number."
    # Condition 2: Short-term storage
        elif area_racks_match:
            try:
                area = float(area_racks_match.group(2))  # Get the area
                total_racks = math.ceil(area / 500)
                return f"Total number of bicycle racks required (short-term): {total_racks}"
            except ValueError:
                logging.error("Invalid value for area in short-term bicycle storage calculation.")
                return "Invalid input for area. Please specify a correct number."

        # If no valid input for either long-term or short-term
        else:
            return "Invalid input for bicycle racks required. Please specify either Building occupants or Area with the appropriate term (long-term or short-term)."

     # Condition: Check for % Improvement calculation
    if Energy_performance_intent:
        if baseline_energy_match and proposed_energy_match:
            try:
                baseline_energy = float(baseline_energy_match.group(1))
                proposed_energy = float(proposed_energy_match.group(1))
                if baseline_energy == 0:
                    return "Baseline Annual Energy Consumption cannot be zero."

            # Calculate percentage improvement
                improvement = math.ceil(((baseline_energy - proposed_energy) / baseline_energy) * 100)
                return f"Percentage Improvement in Energy Consumption: {improvement:.2f}%"
            except ValueError:
                logging.error("Invalid input values for energy consumption.")
                return "Invalid input for energy consumption. Please specify correct numbers."
        else:
            return "Invalid input for Energy performance required.Please specify baseline energy and proposed energy"
    
    # Error messages when incorrect terms are used in storage queries
    if "short-term" in input_text and not (peak_visitors_match or area_match or length_width_match):
        return "Invalid input for short-term storage. Please specify 'Peak visitors = <number>' or 'Area = <number>' with units."
            
    # Error messages when incorrect terms are used in storage queries
    if "short-term" in input_text and not (peak_visitors_match or area_match or length_width_match):
        return "Invalid input for short-term storage. Please specify 'Peak visitors = <number>' or 'Area = <number>' with units."

    if "long-term" in input_text and "regular building occupants" not in input_text:
        return "Invalid input for long-term storage. Please specify 'Regular Building occupants = <number>' with a valid building type."

    # Generic check when 'bicycle storage' is mentioned without specific terms
    if "bicycle storage" in input_text and not (peak_visitors_match or area_match or length_width_match or (building_type_match and (occupants_match or dwelling_units_match))):
        return "No valid numerical data found for required calculation."
    
    if "Preferred space" in input_text and not Total_parking_match:
        return "Invalid input for Preferred space. Please specify 'Total parking spaces = <number>'."

    # Fallback for other inputs
    if not any(char.isdigit() for char in input_text):
        return "No valid number in the response"

    # Default response when input does not match any patterns
    return "No valid numerical data found for required calculation."