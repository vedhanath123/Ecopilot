import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def estimate_materials(analysis_result, project_info):
    """
    Estimate materials based on blueprint analysis and project information.
    
    Args:
        analysis_result: Dictionary with analysis results from blueprint
        project_info: Dictionary with project information
    
    Returns:
        List of dictionaries containing material estimates
    """
    # Get relevant information from analysis result
    building_area_ratio = analysis_result.get('building_area_ratio', 0.5)
    num_rooms = analysis_result.get('num_rooms', 1)
    num_windows_doors = analysis_result.get('num_windows_doors', 2)
    
    # Limit values to reasonable ranges
    MAX_REASONABLE_ROOMS = 30
    MAX_REASONABLE_WINDOWS_DOORS = 60
    MAX_REASONABLE_AREA = 10000  # sq ft
    
    # Apply upper limits to prevent unrealistic values
    num_rooms = min(num_rooms, MAX_REASONABLE_ROOMS)
    num_windows_doors = min(num_windows_doors, MAX_REASONABLE_WINDOWS_DOORS)
    
    # Get project area from project info and apply limit
    area_sqft = project_info.get('area_sqft', 1000)
    area_sqft = min(area_sqft, MAX_REASONABLE_AREA)
    
    # Calculate building area (adjusted by the area ratio from analysis)
    building_area = area_sqft * building_area_ratio
    
    # Initialize materials list
    materials = []
    
    # Concrete estimation
    # Foundation: ~0.5 cubic yards per 100 sq ft
    foundation_concrete = (building_area / 100) * 0.5
    materials.append({
        'name': 'Concrete (Foundation)',
        'quantity': round(foundation_concrete, 2),
        'unit': 'cubic yards',
        'cost': round(foundation_concrete * 125, 2),  # $125 per cubic yard
        'category': 'Concrete'
    })
    
    # Slab: ~4 inches thick for residential
    slab_concrete = (building_area / 100) * 1.23  # 1.23 cubic yards per 100 sq ft at 4 inch thickness
    materials.append({
        'name': 'Concrete (Slab)',
        'quantity': round(slab_concrete, 2),
        'unit': 'cubic yards',
        'cost': round(slab_concrete * 110, 2),  # $110 per cubic yard
        'category': 'Concrete'
    })
    
    # Cement bags (1 cubic yard of concrete needs ~5-6 bags of cement)
    cement_bags = (foundation_concrete + slab_concrete) * 6
    materials.append({
        'name': 'Cement Bags',
        'quantity': round(cement_bags),
        'unit': 'bags',
        'cost': round(cement_bags * 12, 2),  # $12 per bag
        'category': 'Concrete'
    })
    
    # Steel reinforcement (~100 lbs per cubic yard of concrete)
    rebar_weight = (foundation_concrete + slab_concrete) * 100
    materials.append({
        'name': 'Steel Reinforcement',
        'quantity': round(rebar_weight, 2),
        'unit': 'lbs',
        'cost': round(rebar_weight * 0.75, 2),  # $0.75 per lb
        'category': 'Steel'
    })
    
    # Masonry (bricks/blocks)
    # Assuming 10-foot walls and 7.5 blocks per square foot
    wall_area = np.sqrt(building_area) * 4 * 10  # perimeter * height
    blocks_needed = wall_area * 0.75  # 0.75 blocks per sq ft for 8-inch blocks
    materials.append({
        'name': 'Concrete Blocks (8-inch)',
        'quantity': round(blocks_needed),
        'unit': 'blocks',
        'cost': round(blocks_needed * 1.75, 2),  # $1.75 per block
        'category': 'Masonry'
    })
    
    # Mortar for blocks (1 bag per 30-35 blocks)
    mortar_bags = blocks_needed / 32
    materials.append({
        'name': 'Mortar Mix',
        'quantity': round(mortar_bags),
        'unit': 'bags',
        'cost': round(mortar_bags * 9, 2),  # $9 per bag
        'category': 'Masonry'
    })
    
    # Framing lumber
    # ~2 board feet per square foot of building
    lumber_board_feet = building_area * 2
    materials.append({
        'name': 'Framing Lumber',
        'quantity': round(lumber_board_feet),
        'unit': 'board feet',
        'cost': round(lumber_board_feet * 0.85, 2),  # $0.85 per board foot
        'category': 'Other'
    })
    
    # Roof trusses (~1 truss per 2 linear feet of building width)
    building_width = np.sqrt(building_area)
    roof_trusses = building_width / 2
    materials.append({
        'name': 'Roof Trusses',
        'quantity': round(roof_trusses),
        'unit': 'pieces',
        'cost': round(roof_trusses * 85, 2),  # $85 per truss
        'category': 'Other'
    })
    
    # Roofing (assuming asphalt shingles, 1 square = 100 sq ft)
    roof_squares = (building_area * 1.15) / 100  # Adding 15% for roof pitch and overhang
    materials.append({
        'name': 'Asphalt Shingles',
        'quantity': round(roof_squares, 2),
        'unit': 'squares',
        'cost': round(roof_squares * 90, 2),  # $90 per square
        'category': 'Finishing'
    })
    
    # Drywall (4'x8' sheets, ~32 sq ft per sheet)
    # Assuming wall height of 8 feet, plus ceiling
    wall_area = (np.sqrt(building_area) * 4 * 8) + building_area  # perimeter * height + ceiling
    drywall_sheets = wall_area / 32
    materials.append({
        'name': 'Drywall Sheets',
        'quantity': round(drywall_sheets),
        'unit': 'sheets',
        'cost': round(drywall_sheets * 12, 2),  # $12 per sheet
        'category': 'Finishing'
    })
    
    # Flooring (~1.15 factor for waste)
    flooring_area = building_area * 1.15
    materials.append({
        'name': 'Flooring',
        'quantity': round(flooring_area, 2),
        'unit': 'sq ft',
        'cost': round(flooring_area * 3.5, 2),  # $3.50 per sq ft
        'category': 'Finishing'
    })
    
    # Windows (based on detected count and building size, with reasonable limits)
    # Calculate a more reasonable window count based on area and rooms
    # Typical residential buildings have around 1 window per 100-150 sq ft, plus 1-2 per room
    base_window_count = building_area / 150  # Approximately 1 window per 150 sq ft
    room_windows = num_rooms * 1.5  # Average 1-2 windows per room
    
    # Use a weighted average and add a sanity cap
    window_count = min(max(int((base_window_count + room_windows) / 2), 2), 50)  # Between 2 and 50 windows
    
    # For large buildings, ensure window count doesn't exceed a reasonable ratio
    if building_area > 3000:
        window_count = min(window_count, int(building_area / 200))  # 1 window per 200 sq ft for large buildings
    
    materials.append({
        'name': 'Windows',
        'quantity': window_count,
        'unit': 'pieces',
        'cost': round(window_count * 250, 2),  # $250 per window
        'category': 'Finishing'
    })
    
    # Doors (based on building size and rooms with reasonable limits)
    # Typically one door per room plus 1-2 exterior doors
    interior_doors = num_rooms  # 1 door per room
    exterior_doors = min(max(int(np.sqrt(building_area) / 15), 1), 4)  # 1-4 exterior doors based on perimeter
    
    # Total doors with a reasonable maximum
    door_count = min(interior_doors + exterior_doors, 30)  # Cap at 30 doors for very large buildings
    
    materials.append({
        'name': 'Doors',
        'quantity': door_count,
        'unit': 'pieces',
        'cost': round(door_count * 150, 2),  # $150 per door
        'category': 'Finishing'
    })
    
    # Paint (1 gallon per 400 sq ft, 2 coats)
    paint_gallons = (wall_area * 2) / 400
    materials.append({
        'name': 'Paint',
        'quantity': round(paint_gallons, 2),
        'unit': 'gallons',
        'cost': round(paint_gallons * 35, 2),  # $35 per gallon
        'category': 'Finishing'
    })
    
    # Electrical wiring (~200 ft per 1000 sq ft)
    wiring_feet = (building_area / 1000) * 200
    materials.append({
        'name': 'Electrical Wiring',
        'quantity': round(wiring_feet),
        'unit': 'feet',
        'cost': round(wiring_feet * 0.5, 2),  # $0.50 per foot
        'category': 'Other'
    })
    
    # Plumbing (~100 ft per bathroom + 50 ft for kitchen)
    # Assume 1 bathroom per 2 rooms, min 1
    bathroom_count = max(1, num_rooms // 2)
    plumbing_feet = (bathroom_count * 100) + 50
    materials.append({
        'name': 'Plumbing Pipes',
        'quantity': round(plumbing_feet),
        'unit': 'feet',
        'cost': round(plumbing_feet * 2, 2),  # $2 per foot
        'category': 'Other'
    })
    
    # HVAC (basic system cost based on square footage)
    hvac_cost = building_area * 7  # ~$7 per sq ft
    materials.append({
        'name': 'HVAC System',
        'quantity': 1,
        'unit': 'system',
        'cost': round(hvac_cost, 2),
        'category': 'Other'
    })
    
    # Return materials list
    return materials
