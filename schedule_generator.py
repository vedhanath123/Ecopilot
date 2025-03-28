from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_schedule(analysis_result, project_info):
    """
    Generate a day-by-day construction schedule based on blueprint analysis 
    and project information.
    
    Args:
        analysis_result: Dictionary with analysis results from blueprint
        project_info: Dictionary with project information
    
    Returns:
        List of dictionaries containing schedule tasks
    """
    # Memoization cache for expensive calculations
    calculation_cache = {}
    
    # Get project information
    start_date = project_info.get('start_date', datetime.now().date())
    area_sqft = project_info.get('area_sqft', 1000)
    
    # Limit the maximum square footage to prevent unrealistically large projects
    MAX_REASONABLE_SQFT = 10000
    if area_sqft > MAX_REASONABLE_SQFT:
        area_sqft = MAX_REASONABLE_SQFT
    
    # Convert start_date to datetime if it's a date - simpler approach
    if not isinstance(start_date, datetime):
        # Convert any date to datetime in one operation
        try:
            start_date = datetime.combine(start_date, datetime.min.time())
        except (TypeError, AttributeError):
            # Fallback to current date if conversion fails
            start_date = datetime.now()
    
    # Calculate project complexity factors - more efficiently
    building_area_ratio = analysis_result.get('building_area_ratio', 0.5)
    num_rooms = analysis_result.get('num_rooms', 1)
    num_windows_doors = analysis_result.get('num_windows_doors', 2)
    
    # Limit the maximum values to prevent unrealistic complexity
    MAX_ROOMS = 50
    MAX_WINDOWS_DOORS = 100
    num_rooms = min(num_rooms, MAX_ROOMS)
    num_windows_doors = min(num_windows_doors, MAX_WINDOWS_DOORS)
    
    # Simpler calculation with fewer operations and capped complexity
    complexity_factor = 1.0 + (building_area_ratio * 0.5) + (num_rooms * 0.1) + (num_windows_doors * 0.05)
    
    # Limit the maximum complexity factor
    MAX_COMPLEXITY = 3.0
    complexity_factor = min(complexity_factor, MAX_COMPLEXITY)
    
    # Calculate project size factor (larger projects take longer per sq ft)
    size_factor = 1.0
    if area_sqft < 1000:
        size_factor = 0.8
    elif area_sqft > 3000:
        size_factor = 1.2
    
    # Set a reasonable maximum size factor
    MAX_SIZE_FACTOR = 1.5
    size_factor = min(size_factor, MAX_SIZE_FACTOR)
    
    # Helper function to calculate task duration with caching
    def calculate_duration(base_factor, divisor, use_complexity=True, minimum_days=1, maximum_days=30):
        """Calculate task duration with memoization to avoid redundant calculations"""
        cache_key = f"{base_factor}_{divisor}_{use_complexity}_{minimum_days}"
        if cache_key in calculation_cache:
            return calculation_cache[cache_key]
        
        if base_factor == 'sqrt':
            result = max(minimum_days, int(np.sqrt(area_sqft) / divisor))
        else:
            result = max(minimum_days, int(area_sqft / divisor))
            
        if use_complexity:
            result = int(result * complexity_factor)
            
        result = int(result * size_factor)
        
        # Cap the maximum duration of any single task
        result = min(result, maximum_days)
        
        # Cache the result
        calculation_cache[cache_key] = result
        return result
    
    # Initialize schedule
    schedule = []
    current_date = start_date
    
    # Phase 1: Site Preparation and Foundation
    
    # Task 1: Site clearing and preparation
    site_prep_days = calculate_duration('sqrt', 50, use_complexity=False, minimum_days=1)
    end_date = current_date + timedelta(days=site_prep_days)
    schedule.append({
        'task_id': 1,
        'task_name': 'Site Clearing and Preparation',
        'phase': 'Site Preparation',
        'start_date': current_date,
        'end_date': end_date,
        'duration': site_prep_days,
        'responsible_party': 'General Contractor',
        'description': 'Clear site, remove obstacles, grade land',
        'critical_path': True,
        'resources_needed': 'Excavator, Dump Truck, Labor Crew',
        'predecessor_tasks': [],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 2: Excavation
    excavation_days = calculate_duration('sqrt', 50, use_complexity=True, minimum_days=1)
    end_date = current_date + timedelta(days=excavation_days)
    schedule.append({
        'task_id': 2,
        'task_name': 'Excavation',
        'phase': 'Foundation',
        'start_date': current_date,
        'end_date': end_date,
        'duration': excavation_days,
        'responsible_party': 'Excavation Crew',
        'description': 'Excavate foundation area and utility trenches',
        'critical_path': True,
        'resources_needed': 'Excavator, Dump Truck, Labor Crew',
        'predecessor_tasks': [1],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 3: Foundation formwork
    formwork_days = calculate_duration('sqrt', 30, use_complexity=True, minimum_days=2)
    end_date = current_date + timedelta(days=formwork_days)
    schedule.append({
        'task_id': 3,
        'task_name': 'Foundation Formwork',
        'phase': 'Foundation',
        'start_date': current_date,
        'end_date': end_date,
        'duration': formwork_days,
        'responsible_party': 'Concrete Contractor',
        'description': 'Build forms for concrete foundation',
        'critical_path': True,
        'resources_needed': 'Lumber, Form Hardware, Labor Crew',
        'predecessor_tasks': [2],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 4: Steel reinforcement installation
    rebar_days = calculate_duration('sqrt', 70, use_complexity=True, minimum_days=1)
    end_date = current_date + timedelta(days=rebar_days)
    schedule.append({
        'task_id': 4,
        'task_name': 'Steel Reinforcement Installation',
        'phase': 'Foundation',
        'start_date': current_date,
        'end_date': end_date,
        'duration': rebar_days,
        'responsible_party': 'Concrete Contractor',
        'description': 'Install rebar for foundation',
        'critical_path': True,
        'resources_needed': 'Rebar, Tie Wire, Labor Crew',
        'predecessor_tasks': [3],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 5: Foundation concrete pour
    concrete_days = calculate_duration('sqrt', 100, use_complexity=True, minimum_days=1)
    end_date = current_date + timedelta(days=concrete_days)
    schedule.append({
        'task_id': 5,
        'task_name': 'Foundation Concrete Pour',
        'phase': 'Foundation',
        'start_date': current_date,
        'end_date': end_date,
        'duration': concrete_days,
        'responsible_party': 'Concrete Contractor',
        'description': 'Pour concrete for foundation',
        'critical_path': True,
        'resources_needed': 'Concrete, Pump Truck, Labor Crew',
        'predecessor_tasks': [4],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Task 6: Foundation curing
    curing_days = 7  # Standard curing time for concrete
    curing_start = current_date
    curing_end = curing_start + timedelta(days=curing_days)
    schedule.append({
        'task_id': 6,
        'task_name': 'Foundation Curing',
        'phase': 'Foundation',
        'start_date': curing_start,
        'end_date': curing_end,
        'duration': curing_days,
        'responsible_party': 'Concrete Contractor',
        'description': 'Allow concrete to cure properly',
        'critical_path': True,
        'resources_needed': 'Water, Concrete Curing Blankets',
        'predecessor_tasks': [5],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = curing_end + timedelta(days=1)
    
    # Phase 2: Framing
    
    # Task 7: Floor framing
    floor_days = calculate_duration('normal', 500, use_complexity=True, minimum_days=2)
    end_date = current_date + timedelta(days=floor_days)
    schedule.append({
        'task_id': 7,
        'task_name': 'Floor Framing',
        'phase': 'Framing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': floor_days,
        'responsible_party': 'Framing Contractor',
        'description': 'Frame floor structure',
        'critical_path': True,
        'resources_needed': 'Lumber, Nail Gun, Labor Crew',
        'predecessor_tasks': [6],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 8: Wall framing
    wall_days = calculate_duration('normal', 400, use_complexity=True, minimum_days=3)
    end_date = current_date + timedelta(days=wall_days)
    schedule.append({
        'task_id': 8,
        'task_name': 'Wall Framing',
        'phase': 'Framing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': wall_days,
        'responsible_party': 'Framing Contractor',
        'description': 'Frame exterior and interior walls',
        'critical_path': True,
        'resources_needed': 'Lumber, Nail Gun, Labor Crew',
        'predecessor_tasks': [7],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 9: Roof framing
    roof_days = calculate_duration('normal', 500, use_complexity=True, minimum_days=2)
    end_date = current_date + timedelta(days=roof_days)
    schedule.append({
        'task_id': 9,
        'task_name': 'Roof Framing',
        'phase': 'Framing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': roof_days,
        'responsible_party': 'Framing Contractor',
        'description': 'Install roof trusses and framing',
        'critical_path': True,
        'resources_needed': 'Trusses, Lumber, Nail Gun, Labor Crew',
        'predecessor_tasks': [8],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 10: Roofing
    roofing_days = calculate_duration('normal', 600, use_complexity=True, minimum_days=2)
    end_date = current_date + timedelta(days=roofing_days)
    schedule.append({
        'task_id': 10,
        'task_name': 'Roofing Installation',
        'phase': 'Exterior',
        'start_date': current_date,
        'end_date': end_date,
        'duration': roofing_days,
        'responsible_party': 'Roofing Contractor',
        'description': 'Install roof sheathing, underlayment, and shingles',
        'critical_path': True,
        'resources_needed': 'Shingles, Underlayment, Nail Gun, Labor Crew',
        'predecessor_tasks': [9],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Phase 3: Rough-Ins
    
    # Task 11: Window and exterior door installation
    # Using the num_windows_doors for calculation with a custom approach
    window_days = max(1, int(num_windows_doors / 4))
    window_days = int(window_days * complexity_factor * size_factor)
    # Apply the maximum days limit
    window_days = min(window_days, 30)
    end_date = current_date + timedelta(days=window_days)
    schedule.append({
        'task_id': 11,
        'task_name': 'Window and Exterior Door Installation',
        'phase': 'Exterior',
        'start_date': current_date,
        'end_date': end_date,
        'duration': window_days,
        'responsible_party': 'Carpentry Crew',
        'description': 'Install windows and exterior doors',
        'critical_path': False,
        'resources_needed': 'Windows, Doors, Flashing, Labor Crew',
        'predecessor_tasks': [10],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Task 12: Plumbing rough-in (happens concurrently with window installation)
    # Using num_rooms with a custom approach for plumbing calculation
    plumbing_days = max(3, (num_rooms // 2))
    plumbing_days = int(plumbing_days * complexity_factor * size_factor)
    # Apply the maximum days limit
    plumbing_days = min(plumbing_days, 30)
    plumbing_start = current_date
    plumbing_end = plumbing_start + timedelta(days=plumbing_days)
    schedule.append({
        'task_id': 12,
        'task_name': 'Plumbing Rough-in',
        'phase': 'Rough-ins',
        'start_date': plumbing_start,
        'end_date': plumbing_end,
        'duration': plumbing_days,
        'responsible_party': 'Plumbing Contractor',
        'description': 'Install rough plumbing',
        'critical_path': True,
        'resources_needed': 'Pipes, Fittings, Tools, Labor Crew',
        'predecessor_tasks': [9],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Task 13: Electrical rough-in (happens concurrently with window installation)
    electrical_days = calculate_duration('normal', 500, use_complexity=True, minimum_days=3)
    electrical_start = current_date
    electrical_end = electrical_start + timedelta(days=electrical_days)
    schedule.append({
        'task_id': 13,
        'task_name': 'Electrical Rough-in',
        'phase': 'Rough-ins',
        'start_date': electrical_start,
        'end_date': electrical_end,
        'duration': electrical_days,
        'responsible_party': 'Electrical Contractor',
        'description': 'Install rough electrical wiring',
        'critical_path': True,
        'resources_needed': 'Wiring, Boxes, Panels, Labor Crew',
        'predecessor_tasks': [9],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Task 14: HVAC rough-in (happens concurrently with window installation)
    hvac_days = calculate_duration('normal', 700, use_complexity=True, minimum_days=2)
    hvac_start = current_date
    hvac_end = hvac_start + timedelta(days=hvac_days)
    schedule.append({
        'task_id': 14,
        'task_name': 'HVAC Rough-in',
        'phase': 'Rough-ins',
        'start_date': hvac_start,
        'end_date': hvac_end,
        'duration': hvac_days,
        'responsible_party': 'HVAC Contractor',
        'description': 'Install HVAC ductwork and units',
        'critical_path': False,
        'resources_needed': 'Ductwork, HVAC Units, Tools, Labor Crew',
        'predecessor_tasks': [9],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Determine the latest end date among concurrent tasks
    current_date = max(plumbing_end, electrical_end, hvac_end, end_date) + timedelta(days=1)
    
    # Task 15: Insulation installation
    insulation_days = calculate_duration('normal', 1000, use_complexity=True, minimum_days=1)
    end_date = current_date + timedelta(days=insulation_days)
    schedule.append({
        'task_id': 15,
        'task_name': 'Insulation Installation',
        'phase': 'Rough-ins',
        'start_date': current_date,
        'end_date': end_date,
        'duration': insulation_days,
        'responsible_party': 'Insulation Contractor',
        'description': 'Install insulation in walls and ceiling',
        'critical_path': True,
        'resources_needed': 'Insulation, Staple Gun, Labor Crew',
        'predecessor_tasks': [12, 13, 14],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Phase 4: Interior Finishing
    
    # Task 16: Drywall installation
    drywall_days = calculate_duration('normal', 400, use_complexity=True, minimum_days=3)
    end_date = current_date + timedelta(days=drywall_days)
    schedule.append({
        'task_id': 16,
        'task_name': 'Drywall Installation',
        'phase': 'Interior Finishing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': drywall_days,
        'responsible_party': 'Drywall Contractor',
        'description': 'Install and finish drywall',
        'critical_path': True,
        'resources_needed': 'Drywall Sheets, Joint Compound, Tools, Labor Crew',
        'predecessor_tasks': [15],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 17: Interior door installation
    # Using num_rooms with a custom approach for door calculation
    door_days = max(1, (num_rooms // 2))
    door_days = int(door_days * complexity_factor * size_factor)
    # Apply the maximum days limit
    door_days = min(door_days, 20)
    end_date = current_date + timedelta(days=door_days)
    schedule.append({
        'task_id': 17,
        'task_name': 'Interior Door Installation',
        'phase': 'Interior Finishing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': door_days,
        'responsible_party': 'Carpentry Crew',
        'description': 'Install interior doors and trim',
        'critical_path': False,
        'resources_needed': 'Doors, Trim, Nail Gun, Labor Crew',
        'predecessor_tasks': [16],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Task 18: Painting (happens after doors are installed)
    painting_days = calculate_duration('normal', 500, use_complexity=True, minimum_days=3)
    painting_start = end_date + timedelta(days=1)
    painting_end = painting_start + timedelta(days=painting_days)
    schedule.append({
        'task_id': 18,
        'task_name': 'Painting',
        'phase': 'Interior Finishing',
        'start_date': painting_start,
        'end_date': painting_end,
        'duration': painting_days,
        'responsible_party': 'Painting Contractor',
        'description': 'Prime and paint walls and ceilings',
        'critical_path': True,
        'resources_needed': 'Paint, Brushes, Rollers, Labor Crew',
        'predecessor_tasks': [17],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = painting_end + timedelta(days=1)
    
    # Task 19: Flooring installation
    flooring_days = calculate_duration('normal', 500, use_complexity=True, minimum_days=2)
    end_date = current_date + timedelta(days=flooring_days)
    schedule.append({
        'task_id': 19,
        'task_name': 'Flooring Installation',
        'phase': 'Interior Finishing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': flooring_days,
        'responsible_party': 'Flooring Contractor',
        'description': 'Install flooring throughout the building',
        'critical_path': True,
        'resources_needed': 'Flooring Materials, Tools, Labor Crew',
        'predecessor_tasks': [18],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 20: Cabinetry and countertop installation
    # Using num_rooms for cabinet calculation
    cabinet_days = max(2, (num_rooms // 3))
    cabinet_days = int(cabinet_days * complexity_factor * size_factor)
    # Apply the maximum days limit
    cabinet_days = min(cabinet_days, 15)
    end_date = current_date + timedelta(days=cabinet_days)
    schedule.append({
        'task_id': 20,
        'task_name': 'Cabinetry and Countertop Installation',
        'phase': 'Interior Finishing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': cabinet_days,
        'responsible_party': 'Cabinet Installer',
        'description': 'Install kitchen and bathroom cabinets and countertops',
        'critical_path': True,
        'resources_needed': 'Cabinets, Countertops, Tools, Labor Crew',
        'predecessor_tasks': [19],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Phase 5: Final Finishing
    
    # Task 21: Plumbing fixtures installation
    # Using num_rooms with a custom approach for plumbing fixtures
    plumbing_fixture_days = max(1, (num_rooms // 3))
    plumbing_fixture_days = int(plumbing_fixture_days * size_factor)  # Use only size factor for finishing work
    # Apply the maximum days limit
    plumbing_fixture_days = min(plumbing_fixture_days, 10)
    end_date = current_date + timedelta(days=plumbing_fixture_days)
    schedule.append({
        'task_id': 21,
        'task_name': 'Plumbing Fixtures Installation',
        'phase': 'Final Finishing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': plumbing_fixture_days,
        'responsible_party': 'Plumbing Contractor',
        'description': 'Install sinks, toilets, faucets, and other plumbing fixtures',
        'critical_path': False,
        'resources_needed': 'Fixtures, Tools, Labor Crew',
        'predecessor_tasks': [20],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Task 22: Electrical fixtures installation (concurrent with plumbing fixtures)
    # Use more efficient calculation for electrical fixtures
    electrical_fixture_days = calculate_duration('normal', 1000, use_complexity=False, minimum_days=1)
    electrical_fixture_start = current_date
    electrical_fixture_end = electrical_fixture_start + timedelta(days=electrical_fixture_days)
    schedule.append({
        'task_id': 22,
        'task_name': 'Electrical Fixtures Installation',
        'phase': 'Final Finishing',
        'start_date': electrical_fixture_start,
        'end_date': electrical_fixture_end,
        'duration': electrical_fixture_days,
        'responsible_party': 'Electrical Contractor',
        'description': 'Install light fixtures, outlets, switches, and electrical panels',
        'critical_path': False,
        'resources_needed': 'Fixtures, Tools, Labor Crew',
        'predecessor_tasks': [20],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Determine the latest end date among concurrent tasks
    current_date = max(end_date, electrical_fixture_end) + timedelta(days=1)
    
    # Task 23: Appliance installation - fixed duration task
    appliance_days = 1  # Simple fixed duration
    end_date = current_date + timedelta(days=appliance_days)
    schedule.append({
        'task_id': 23,
        'task_name': 'Appliance Installation',
        'phase': 'Final Finishing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': appliance_days,
        'responsible_party': 'General Contractor',
        'description': 'Install kitchen and laundry appliances',
        'critical_path': True,
        'resources_needed': 'Appliances, Tools, Labor Crew',
        'predecessor_tasks': [21, 22],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 24: Final cleaning
    # Simpler calculation for cleaning
    cleaning_days = calculate_duration('normal', 2000, use_complexity=False, minimum_days=1)
    end_date = current_date + timedelta(days=cleaning_days)
    schedule.append({
        'task_id': 24,
        'task_name': 'Final Cleaning',
        'phase': 'Final Finishing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': cleaning_days,
        'responsible_party': 'Cleaning Crew',
        'description': 'Clean entire building interior and exterior',
        'critical_path': True,
        'resources_needed': 'Cleaning Supplies, Labor Crew',
        'predecessor_tasks': [23],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    current_date = end_date + timedelta(days=1)
    
    # Task 25: Final inspection - fixed duration task
    inspection_days = 1  # Simple fixed duration
    end_date = current_date + timedelta(days=inspection_days)
    schedule.append({
        'task_id': 25,
        'task_name': 'Final Inspection',
        'phase': 'Final Finishing',
        'start_date': current_date,
        'end_date': end_date,
        'duration': inspection_days,
        'responsible_party': 'Building Inspector',
        'description': 'Final inspection and certificate of occupancy',
        'critical_path': True,
        'resources_needed': 'Inspector',
        'predecessor_tasks': [24],
        'manual_completion_pct': None  # Field for manual completion percentage
    })
    
    # Return the schedule
    # Add task dependencies and convert predecessor_tasks IDs to task names
    for task in schedule:
        # Convert task IDs to task names for dependencies
        dependencies = []
        for pred_id in task.get('predecessor_tasks', []):
            pred_task = next((t for t in schedule if t['task_id'] == pred_id), None)
            if pred_task:
                dependencies.append(pred_task['task_name'])
        
        # Add dependencies to the task
        task['dependencies'] = dependencies
        
        # Add a completion percentage based on current date
        today = datetime.now().date()
        
        # Convert datetime to date for comparison if needed
        end_date = task['end_date'].date() if hasattr(task['end_date'], 'date') else task['end_date']
        start_date = task['start_date'].date() if hasattr(task['start_date'], 'date') else task['start_date']
        
        if end_date < today:
            # Task should be complete
            task['completion_percentage'] = 100
        elif start_date > today:
            # Task hasn't started yet
            task['completion_percentage'] = 0
        else:
            # Task is in progress
            total_days = (end_date - start_date).days
            days_passed = (today - start_date).days
            if total_days > 0:
                completion = int((days_passed / total_days) * 100)
                task['completion_percentage'] = min(100, max(0, completion))
            else:
                task['completion_percentage'] = 50
    
    return schedule
