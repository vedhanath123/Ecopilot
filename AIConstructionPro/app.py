import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.colors as pc
from datetime import date, datetime, timedelta
import os
import io
from PIL import Image

# Import custom modules
from utils.image_processing import preprocess_image, extract_features
from utils.material_estimation import estimate_materials
from utils.schedule_generator import generate_schedule
from ai_models.blueprint_analyzer import analyze_blueprint

# Helper function for consistent date handling throughout the application
def get_date(date_obj):
    """
    Convert various date formats to a consistent date object.
    Works with datetime objects, date objects, and date strings.
    
    Args:
        date_obj: A date in various formats (datetime, date, or string)
        
    Returns:
        A date object (not datetime)
    """
    # If it's a string, convert to datetime then date
    if isinstance(date_obj, str):
        return datetime.strptime(date_obj, '%Y-%m-%d').date()
    # If it's a datetime, convert to date
    elif hasattr(date_obj, 'date'):
        return date_obj.date()
    # If it's already a date, return as is
    return date_obj

# Set page configuration
st.set_page_config(
    page_title="Construction Analyzer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define the session state variables if they don't exist
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'materials' not in st.session_state:
    st.session_state.materials = None
if 'schedule' not in st.session_state:
    st.session_state.schedule = None
if 'project_info' not in st.session_state:
    st.session_state.project_info = {
        'name': 'Sample Construction Project',
        'location': 'New York, NY',
        'start_date': datetime.now().date(),
        'contractor': 'ABC Construction Co.',
        'area_sqft': 2500
    }

# Sidebar for project information
with st.sidebar:
    st.title("Project Information")
    
    st.session_state.project_info['name'] = st.text_input("Project Name", st.session_state.project_info['name'])
    st.session_state.project_info['location'] = st.text_input("Location", st.session_state.project_info['location'])
    st.session_state.project_info['start_date'] = st.date_input("Start Date", st.session_state.project_info['start_date'])
    st.session_state.project_info['contractor'] = st.text_input("Contractor", st.session_state.project_info['contractor'])
    st.session_state.project_info['area_sqft'] = st.number_input("Total Area (sq ft)", min_value=0, value=st.session_state.project_info['area_sqft'])
    
    st.divider()
    
    # Application information
    st.subheader("About")
    st.markdown("""
    This application uses AI to analyze construction drawings, estimate material requirements, and generate construction schedules.
    
    Upload a blueprint to get started.
    """)

# Main content
st.title("AI-Powered Construction Analyzer")

# Create tabs for different sections of the application
tab1, tab2, tab3, tab4 = st.tabs(["Blueprint Upload", "Material Estimation", "Construction Schedule", "Export Results"])

# Tab 1: Blueprint Upload
with tab1:
    st.header("Upload Construction Blueprint")
    
    # Upload section first for better performance
    st.subheader("Upload Your Blueprint")
    uploaded_file = st.file_uploader("Choose a blueprint image...", type=["jpg", "jpeg", "png"])
    
    # Option to show/hide examples to improve performance
    show_examples = st.checkbox("Show Example Blueprints", value=False)
    
    # Display example blueprints only if requested
    if show_examples:
        st.subheader("Example Blueprints")
        
        with st.spinner("Loading example images..."):
            col1, col2 = st.columns(2)
            with col1:
                st.image("https://images.unsplash.com/photo-1503387837-b154d5074bd2", 
                        caption="Construction Blueprint Example 1", use_container_width=True)
                st.image("https://images.unsplash.com/photo-1503387762-592deb58ef4e", 
                        caption="Construction Blueprint Example 3", use_container_width=True)
            with col2:
                st.image("https://images.unsplash.com/photo-1627660080110-20045fd3875d", 
                        caption="Construction Blueprint Example 2", use_container_width=True)
                st.image("https://images.unsplash.com/photo-1542621334-a254cf47733d", 
                        caption="Construction Blueprint Example 4", use_container_width=True)
    
    if uploaded_file is not None:
        # Save the uploaded image
        image = Image.open(uploaded_file)
        st.session_state.uploaded_image = image
        
        # Show the uploaded image
        st.image(image, caption="Uploaded Blueprint", use_container_width=True)
        
        # Process button
        if st.button("Process Blueprint"):
            with st.spinner("Analyzing blueprint..."):
                # Preprocess the image
                processed_img = preprocess_image(image)
                st.session_state.processed_image = processed_img
                
                # Extract features
                features = extract_features(processed_img)
                
                # Analyze the blueprint
                analysis_result = analyze_blueprint(features)
                
                # Estimate materials
                materials = estimate_materials(analysis_result, st.session_state.project_info)
                st.session_state.materials = materials
                
                # Generate schedule
                schedule = generate_schedule(analysis_result, st.session_state.project_info)
                st.session_state.schedule = schedule
                
                st.success("Blueprint analysis complete! Check the Material Estimation and Construction Schedule tabs.")

# Tab 2: Material Estimation
with tab2:
    st.header("Material Estimation")
    
    if st.session_state.materials is None:
        st.info("Please upload and process a blueprint first.")
        
        # Option to show/hide examples to improve performance
        show_examples = st.checkbox("Show Example Building Materials", value=False)
        
        # Display example construction materials only if requested
        if show_examples:
            st.subheader("Example Building Materials")
            with st.spinner("Loading example images..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.image("https://images.unsplash.com/photo-1627882206813-8c1ffd86efec", 
                            caption="Building Materials Example 1", use_container_width=True)
                    st.image("https://images.unsplash.com/photo-1595414440701-da000c40df9c", 
                            caption="Building Materials Example 3", use_container_width=True)
                with col2:
                    st.image("https://images.unsplash.com/photo-1609867271967-a82f85c48531", 
                            caption="Building Materials Example 2", use_container_width=True)
                    st.image("https://images.unsplash.com/photo-1504307651254-35680f356dfd", 
                            caption="Building Materials Example 4", use_container_width=True)
    else:
        # Add settings for currency and unit conversion
        st.subheader("Settings")
        
        settings_col1, settings_col2 = st.columns(2)
        
        # Currency selection
        with settings_col1:
            # Currency conversion rates (USD to other currencies)
            currency_rates = {
                "USD": 1.0,
                "INR": 83.5,  # Indian Rupee
                "EUR": 0.92,  # Euro
                "GBP": 0.79,  # British Pound
                "JPY": 151.2, # Japanese Yen
                "CNY": 7.22,  # Chinese Yuan
                "AUD": 1.50,  # Australian Dollar
                "CAD": 1.36,  # Canadian Dollar
            }
            
            currency_symbols = {
                "USD": "$",
                "INR": "₹",
                "EUR": "€",
                "GBP": "£",
                "JPY": "¥",
                "CNY": "¥",
                "AUD": "A$",
                "CAD": "C$",
            }
            
            selected_currency = st.selectbox(
                "Select Currency:", 
                options=list(currency_rates.keys()),
                format_func=lambda x: f"{x} ({currency_symbols[x]})",
                index=1  # Default to INR
            )
            
            # Store the conversion rate
            conversion_rate = currency_rates[selected_currency]
            currency_symbol = currency_symbols[selected_currency]
            
        # Unit conversion selection
        with settings_col2:
            # Unit conversion options and rates
            unit_conversions = {
                "No Conversion": {
                    "cubic yards": (1.0, "cubic yards"),
                    "sq ft": (1.0, "sq ft"),
                    "linear feet": (1.0, "linear feet"),
                    "pieces": (1.0, "pieces"),
                    "tons": (1.0, "tons"),
                    "gallons": (1.0, "gallons")
                },
                "Metric": {
                    "cubic yards": (0.764555, "cubic meters"),
                    "sq ft": (0.092903, "sq meters"),
                    "linear feet": (0.3048, "meters"),
                    "pieces": (1.0, "pieces"),
                    "tons": (0.907185, "tonnes"),
                    "gallons": (3.78541, "liters")
                },
                "Imperial (UK)": {
                    "cubic yards": (0.764555, "cubic yards"),
                    "sq ft": (0.092903, "sq feet"),
                    "linear feet": (0.3048, "feet"),
                    "pieces": (1.0, "pieces"),
                    "tons": (1.0, "tons"),
                    "gallons": (0.832674, "imp. gallons")
                }
            }
            
            selected_unit_system = st.selectbox(
                "Select Unit System:",
                options=list(unit_conversions.keys()),
                index=1  # Default to Metric
            )
            
            # Store the unit conversion dictionary
            unit_converters = unit_conversions[selected_unit_system]
        
        # Function to convert material values based on settings
        def convert_material(item):
            # Copy the original item
            converted_item = item.copy()
            
            # Apply currency conversion to cost
            if 'cost' in item:
                converted_item['cost'] = item['cost'] * conversion_rate
            
            # Apply currency conversion to cost_per_unit if it exists
            if 'cost_per_unit' in item:
                converted_item['cost_per_unit'] = item['cost_per_unit'] * conversion_rate
            else:
                # Calculate cost per unit if not present
                if 'cost' in item and 'quantity' in item and item['quantity'] > 0:
                    converted_item['cost_per_unit'] = item['cost'] / item['quantity']
                else:
                    converted_item['cost_per_unit'] = 0
            
            # Apply unit conversion if needed
            if 'unit' in item:
                original_unit = item['unit']
                if original_unit in unit_converters:
                    factor, new_unit = unit_converters[original_unit]
                    if 'quantity' in item:
                        converted_item['quantity'] = item['quantity'] * factor
                    converted_item['unit'] = new_unit
                    # Adjust cost per unit based on the new unit
                    if 'cost_per_unit' in converted_item and factor > 0:
                        converted_item['cost_per_unit'] = converted_item['cost_per_unit'] / factor
            
            # Format cost values for display
            if 'cost' in converted_item:
                converted_item['display_cost'] = f"{currency_symbol}{converted_item['cost']:,.2f}"
            if 'cost_per_unit' in converted_item:
                converted_item['display_cost_per_unit'] = f"{currency_symbol}{converted_item['cost_per_unit']:,.2f}"
            
            return converted_item
            
        # Convert all materials based on selected currency and units
        converted_materials = [convert_material(item) for item in st.session_state.materials]
        
        # Create material categories
        concrete_materials = [item for item in converted_materials if item['category'] == 'Concrete']
        steel_materials = [item for item in converted_materials if item['category'] == 'Steel']
        masonry_materials = [item for item in converted_materials if item['category'] == 'Masonry']
        finishing_materials = [item for item in converted_materials if item['category'] == 'Finishing']
        other_materials = [item for item in converted_materials if item['category'] == 'Other']
        
        # Add a note about conversions
        st.info(f"💡 Note: All costs are shown in {selected_currency} ({currency_symbol}) and measurements in {selected_unit_system} system. Original data remains unchanged in the system.")
        
        # Create tabs for material categories
        mat_tab1, mat_tab2, mat_tab3, mat_tab4, mat_tab5 = st.tabs(["Concrete", "Steel", "Masonry", "Finishing", "Other"])
        
        with mat_tab1:
            st.subheader("Concrete Materials")
            if concrete_materials:
                df = pd.DataFrame(concrete_materials)
                st.dataframe(df, use_container_width=True)
                
                # Create a pie chart for concrete materials
                fig = px.pie(df, values='quantity', names='name', title='Concrete Materials Distribution')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No concrete materials estimated for this project.")
                
        with mat_tab2:
            st.subheader("Steel Materials")
            if steel_materials:
                df = pd.DataFrame(steel_materials)
                st.dataframe(df, use_container_width=True)
                
                # Create a bar chart for steel materials
                # Simplified steel materials bar chart
                fig = px.bar(
                    df, 
                    x='name', 
                    y='quantity', 
                    title='Steel Materials Quantities',
                    color_discrete_sequence=['#1f77b4']  # Single blue color
                )
                fig.update_layout(
                    xaxis_title="Material Name", 
                    yaxis_title="Quantity",
                    showlegend=False,  # Remove legend
                    plot_bgcolor='white'  # Clean white background
                )
                # Simplify bar appearance
                fig.update_traces(
                    marker_line_width=1,
                    marker_line_color="white",
                    opacity=0.8
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No steel materials estimated for this project.")
                
        with mat_tab3:
            st.subheader("Masonry Materials")
            if masonry_materials:
                df = pd.DataFrame(masonry_materials)
                st.dataframe(df, use_container_width=True)
                
                # Create a bar chart for masonry materials
                # Simplified masonry materials bar chart
                fig = px.bar(
                    df, 
                    x='name', 
                    y='quantity', 
                    title='Masonry Materials Quantities',
                    color_discrete_sequence=['#ff7f0e']  # Single orange color
                )
                fig.update_layout(
                    xaxis_title="Material Name", 
                    yaxis_title="Quantity",
                    showlegend=False,  # Remove legend
                    plot_bgcolor='white'  # Clean white background
                )
                # Simplify bar appearance
                fig.update_traces(
                    marker_line_width=1,
                    marker_line_color="white",
                    opacity=0.8
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No masonry materials estimated for this project.")
                
        with mat_tab4:
            st.subheader("Finishing Materials")
            if finishing_materials:
                df = pd.DataFrame(finishing_materials)
                st.dataframe(df, use_container_width=True)
                
                # Create a bar chart for finishing materials
                # Simplified finishing materials bar chart
                fig = px.bar(
                    df, 
                    x='name', 
                    y='quantity', 
                    title='Finishing Materials Quantities',
                    color_discrete_sequence=['#2ca02c']  # Single green color
                )
                fig.update_layout(
                    xaxis_title="Material Name", 
                    yaxis_title="Quantity",
                    showlegend=False,  # Remove legend
                    plot_bgcolor='white'  # Clean white background
                )
                # Simplify bar appearance
                fig.update_traces(
                    marker_line_width=1,
                    marker_line_color="white",
                    opacity=0.8
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No finishing materials estimated for this project.")
                
        with mat_tab5:
            st.subheader("Other Materials")
            if other_materials:
                df = pd.DataFrame(other_materials)
                st.dataframe(df, use_container_width=True)
                
                # Create a bar chart for other materials
                # Simplified other materials bar chart
                fig = px.bar(
                    df, 
                    x='name', 
                    y='quantity', 
                    title='Other Materials Quantities',
                    color_discrete_sequence=['#9467bd']  # Single purple color
                )
                fig.update_layout(
                    xaxis_title="Material Name", 
                    yaxis_title="Quantity",
                    showlegend=False,  # Remove legend
                    plot_bgcolor='white'  # Clean white background
                )
                # Simplify bar appearance
                fig.update_traces(
                    marker_line_width=1,
                    marker_line_color="white",
                    opacity=0.8
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No other materials estimated for this project.")
        
        # Total cost calculation and display
        total_cost = sum(item.get('cost', 0) for item in converted_materials)
        st.metric("Total Estimated Material Cost", f"{currency_symbol}{total_cost:,.2f}")
        
        # Display a cost breakdown
        st.subheader("Cost Breakdown by Category")
        cost_by_category = {}
        for item in converted_materials:
            if item['category'] not in cost_by_category:
                cost_by_category[item['category']] = 0
            cost_by_category[item['category']] += item.get('cost', 0)
        
        cost_df = pd.DataFrame({
            'Category': list(cost_by_category.keys()),
            'Cost': list(cost_by_category.values())
        })
        
        fig = px.pie(cost_df, values='Cost', names='Category', title=f'Material Cost Distribution ({currency_symbol})')
        st.plotly_chart(fig, use_container_width=True)

# Tab 3: Construction Schedule
with tab3:
    st.header("Construction Schedule")
    
    if st.session_state.schedule is None:
        st.info("Please upload and process a blueprint first.")
        
        # Option to show/hide examples to improve performance
        show_examples = st.checkbox("Show Construction Examples", value=False)
        
        # Display example construction sites and schedules only if requested
        if show_examples:
            with st.spinner("Loading example images..."):
                st.subheader("Example Construction Progress")
                col1, col2 = st.columns(2)
                with col1:
                    st.image("https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122", 
                            caption="Construction Site Example 1", use_container_width=True)
                    st.image("https://images.unsplash.com/photo-1489514354504-1653aa90e34e", 
                            caption="Construction Site Example 3", use_container_width=True)
                with col2:
                    st.image("https://images.unsplash.com/photo-1541888946425-d81bb19240f5", 
                            caption="Construction Site Example 2", use_container_width=True)
                    st.image("https://images.unsplash.com/photo-1429497419816-9ca5cfb4571a", 
                            caption="Construction Site Example 4", use_container_width=True)
                    
                st.subheader("Example Schedule Charts")
                col1, col2 = st.columns(2)
                with col1:
                    st.image("https://images.unsplash.com/photo-1541888946425-d81bb19240f5", 
                            caption="Schedule Chart Example 1", use_container_width=True)
                    st.image("https://images.unsplash.com/photo-1429497419816-9ca5cfb4571a", 
                            caption="Schedule Chart Example 3", use_container_width=True)
                with col2:
                    st.image("https://images.unsplash.com/photo-1489514354504-1653aa90e34e", 
                            caption="Schedule Chart Example 2", use_container_width=True)
                    st.image("https://images.unsplash.com/photo-1531834685032-c34bf0d84c77", 
                            caption="Schedule Chart Example 4", use_container_width=True)
    else:
        # Convert schedule to DataFrame
        df = pd.DataFrame(st.session_state.schedule)
        
        # Display the schedule with editable completion percentages
        st.subheader("Detailed Construction Schedule")
        
        # Add a toggle for choosing between auto calculation and manual entry
        if 'completion_mode' not in st.session_state:
            st.session_state.completion_mode = "Auto-calculate based on dates"
            
        if 'using_manual_completion' not in st.session_state:
            st.session_state.using_manual_completion = False
            
        completion_mode = st.radio(
            "Completion Percentage Mode:",
            ["Auto-calculate based on dates", "Enter manually"],
            key="completion_mode_radio", 
            horizontal=True,
            index=0 if st.session_state.completion_mode == "Auto-calculate based on dates" else 1
        )
        
        # Update session state
        st.session_state.completion_mode = completion_mode
        
        # Display explanation based on mode
        if completion_mode == "Auto-calculate based on dates":
            st.info("📅 Task completion percentages are automatically calculated based on today's date and the scheduled task dates.")
            # If switching from manual to auto, disable manual mode
            if st.session_state.using_manual_completion:
                st.session_state.using_manual_completion = False
        else:
            st.info("✏️ Manually adjust completion percentages for each task below.")
        
        # Display the schedule dataframe (read-only)
        st.dataframe(df, use_container_width=True)
        
        # If manual mode, show editable inputs for each task
        if completion_mode == "Enter manually":
            # Initialize manual_completion if needed
            if 'manual_completion' not in st.session_state:
                st.session_state.manual_completion = {}
                # Initialize once with calculated values
                for i, task in enumerate(st.session_state.schedule):
                    task_id = f"{i}_{task['task_name'].replace(' ', '_')}"
                    
                    # Calculate initial completion percentage (simple version)
                    start = get_date(task['start_date'])
                    end = get_date(task['end_date'])
                    today = datetime.now().date()
                    
                    if today < start:
                        auto_completion = 0
                    elif today > end:
                        auto_completion = 100
                    else:
                        duration = max(1, (end - start).days)
                        days_passed = (today - start).days
                        auto_completion = min(100, max(0, int((days_passed / duration) * 100)))
                    
                    # Store the auto-calculated value
                    st.session_state.manual_completion[task_id] = auto_completion
            
            # Create expanders for each phase to group tasks
            phases = sorted(list(set(task['phase'] for task in st.session_state.schedule)))
            
            for phase in phases:
                with st.expander(f"Phase: {phase}", expanded=False):
                    # Get tasks for this phase
                    phase_tasks = [(i, task) for i, task in enumerate(st.session_state.schedule) if task['phase'] == phase]
                    
                    # Create a grid of sliders with fewer columns for better performance
                    cols_per_row = 2  # Reduced from 3 to 2 for better performance
                    
                    # Group tasks into rows
                    for i in range(0, len(phase_tasks), cols_per_row):
                        # Create columns for this row
                        cols = st.columns(cols_per_row)
                        
                        # Add tasks to each column
                        for j in range(cols_per_row):
                            if i + j < len(phase_tasks):
                                task_idx, task = phase_tasks[i + j]
                                task_id = f"{task_idx}_{task['task_name'].replace(' ', '_')}"
                                
                                with cols[j]:
                                    # Create a unique key for each slider
                                    st.session_state.manual_completion[task_id] = st.slider(
                                        f"{task['task_name']}",
                                        0, 100, 
                                        st.session_state.manual_completion.get(task_id, 0),
                                        key=f"completion_{task_id}"
                                    )
            
            # Display a summary visualization of completion percentages by phase
            st.subheader("Phase Completion Summary")
            
            # Group tasks by phase and calculate average completion percentage
            phase_completion = {}
            for i, task in enumerate(st.session_state.schedule):
                phase = task['phase']
                task_id = f"{i}_{task['task_name'].replace(' ', '_')}"
                
                if phase not in phase_completion:
                    phase_completion[phase] = {'total': 0, 'count': 0, 'tasks': []}
                
                completion_value = st.session_state.manual_completion.get(task_id, 0)
                phase_completion[phase]['total'] += completion_value
                phase_completion[phase]['count'] += 1
                phase_completion[phase]['tasks'].append({
                    'Task': task['task_name'],
                    'Completion': completion_value
                })
            
            # Calculate average for each phase and prepare data for charts
            summary_data = []
            task_level_data = []
            
            for phase, data in phase_completion.items():
                if data['count'] > 0:
                    avg_percentage = data['total'] / data['count']
                    summary_data.append({
                        'Phase': phase,
                        'Average Completion': avg_percentage,
                        'Number of Tasks': data['count']
                    })
                    
                    # Add individual task data for this phase
                    for task_data in data['tasks']:
                        task_level_data.append({
                            'Phase': phase,
                            'Task': task_data['Task'],
                            'Completion': task_data['Completion']
                        })
            
            # Create summary visualization
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                
                # Create a colorful bar chart for phase completion percentages
                fig = px.bar(
                    summary_df,
                    x='Phase',
                    y='Average Completion',
                    title='Average Completion Percentage by Phase',
                    text='Average Completion',
                    color='Average Completion',
                    color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
                    range_color=[0, 100],
                    hover_data=['Number of Tasks']
                )
                
                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    marker_line_width=1.5,
                    marker_line_color='white'
                )
                
                fig.update_layout(
                    yaxis_range=[0, 105],  # Set y-axis range from 0 to 105 to make room for labels
                    yaxis_title='Completion Percentage',
                    xaxis_title='Construction Phase',
                    coloraxis_showscale=False,
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Also create a detailed task-level heatmap if there are many tasks
                if len(task_level_data) > 5:
                    task_df = pd.DataFrame(task_level_data)
                    
                    # Create a heatmap of task completion by phase
                    fig2 = px.density_heatmap(
                        task_df,
                        x='Phase',
                        y='Task',
                        z='Completion',
                        title='Task Completion Heatmap',
                        color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
                        range_color=[0, 100]
                    )
                    
                    fig2.update_layout(
                        xaxis_title='Construction Phase',
                        yaxis_title='Task',
                        coloraxis_colorbar=dict(title='Completion %'),
                        height=400
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Button to apply manual percentages to the schedule
            if st.button("Apply Completion Percentages", type="primary"):
                # Update the completion percentages in the schedule
                with st.spinner("Applying completion percentages..."):
                    for i, task in enumerate(st.session_state.schedule):
                        task_id = f"{i}_{task['task_name'].replace(' ', '_')}"
                        task['manual_completion'] = st.session_state.manual_completion[task_id]
                
                st.success("✅ Completion percentages have been applied to the schedule!")
                st.session_state.using_manual_completion = True
        
        # Create an enhanced 3D construction timeline visualization
        st.subheader("3D Construction Timeline Visualization")
        
        # We'll use the global get_date function defined at the top of the file
        
        # Get the earliest and latest dates from the schedule
        all_start_dates = [get_date(task['start_date']) for task in st.session_state.schedule]
        all_end_dates = [get_date(task['end_date']) for task in st.session_state.schedule]
        min_date = min(all_start_dates) - timedelta(days=7)  # A week before the earliest task
        max_date = max(all_end_dates) + timedelta(days=7)    # A week after the latest task
        today = datetime.now().date()
        
        # Create a container for the calendar date selectors
        st.write("### Select Custom Date Range")
        calendar_cols = st.columns(2)
        
        # Initialize session state variables for date range if they don't exist
        if 'schedule_view_start_date' not in st.session_state:
            st.session_state.schedule_view_start_date = today
        if 'schedule_view_end_date' not in st.session_state:
            # Default to show 1 month ahead
            st.session_state.schedule_view_end_date = today + timedelta(days=30)
        
        # Display calendars for date selection
        with calendar_cols[0]:
            start_date = st.date_input(
                "From Date:", 
                value=st.session_state.schedule_view_start_date,
                min_value=min_date,
                max_value=max_date,
                key="start_date_calendar"
            )
            st.session_state.schedule_view_start_date = start_date
        
        with calendar_cols[1]:
            # Ensure end date is always after or equal to start date and within valid range
            # First make sure schedule_view_end_date is within the valid range
            valid_end_date = min(st.session_state.schedule_view_end_date, max_date)
            valid_end_date = max(valid_end_date, start_date)
            
            end_date = st.date_input(
                "To Date:", 
                value=valid_end_date,
                min_value=start_date,
                max_value=max_date,
                key="end_date_calendar"
            )
            st.session_state.schedule_view_end_date = end_date
        
        # Create quick selection buttons
        st.write("### Quick Selection")
        time_filter_cols = st.columns(5)
        
        with time_filter_cols[0]:
            if st.button("1 Week", help="Show only tasks in the next week"):
                st.session_state.schedule_view_start_date = today
                st.session_state.schedule_view_end_date = today + timedelta(days=7)
                # Need to rerun to update the date inputs
                st.rerun()
                
        with time_filter_cols[1]:
            if st.button("1 Month", help="Show only tasks in the next month"):
                st.session_state.schedule_view_start_date = today
                st.session_state.schedule_view_end_date = today + timedelta(days=30)
                st.rerun()
                
        with time_filter_cols[2]:
            if st.button("6 Months", help="Show only tasks in the next 6 months"):
                st.session_state.schedule_view_start_date = today
                st.session_state.schedule_view_end_date = today + timedelta(days=180)
                st.rerun()
                
        with time_filter_cols[3]:
            if st.button("Year to Date", help="Show tasks from the start of the year"):
                st.session_state.schedule_view_start_date = datetime(today.year, 1, 1).date()
                st.session_state.schedule_view_end_date = max_date
                st.rerun()
                
        with time_filter_cols[4]:
            if st.button("Full Timeline", help="Show the full project timeline"):
                st.session_state.schedule_view_start_date = min_date
                st.session_state.schedule_view_end_date = max_date
                st.rerun()

        # Filter the schedule based on the selected date range
        filtered_schedule = [
            task for task in st.session_state.schedule.copy() 
            if (
                # Task starts before or on end_date AND ends on or after start_date
                get_date(task['start_date']) <= end_date and 
                get_date(task['end_date']) >= start_date
            )
        ]
        
        # Show the selected date range
        date_format = "%B %d, %Y"  # Format like "January 15, 2025"
        st.info(f"Showing tasks from **{start_date.strftime(date_format)}** to **{end_date.strftime(date_format)}**")
            
        # Add resource filter
        resources = sorted(list(set(task['responsible_party'] for task in filtered_schedule)))
        selected_resources = st.multiselect(
            "Filter by Responsible Party:",
            options=resources,
            default=resources
        )
        
        # Filter by selected resources
        if selected_resources:
            filtered_schedule = [task for task in filtered_schedule 
                              if task['responsible_party'] in selected_resources]
        
        # Add phase filter
        phases = sorted(list(set(task['phase'] for task in filtered_schedule)))
        selected_phases = st.multiselect(
            "Filter by Construction Phase:",
            options=phases,
            default=phases
        )
        
        # Filter by selected phases
        if selected_phases:
            filtered_schedule = [task for task in filtered_schedule 
                              if task['phase'] in selected_phases]
        
        if not filtered_schedule:
            st.warning("No tasks match the selected filters. Please adjust your filter settings.")
        else:
            # Create a custom colorscale with enough colors
            import plotly.colors as pc
            colors = pc.qualitative.Plotly[:] + pc.qualitative.D3[:] + pc.qualitative.G10[:] + pc.qualitative.T10[:]
            
            # 3D Timeline visualization - main visualization
            
            # Create an infographic dataset with 3D coordinates
            today = datetime.now().date()
            
            # Add a debug message
            st.write(f"Current date for calculations: {today}")
            
            # Group tasks by phase for cleaner presentation
            phases = sorted(list(set(task['phase'] for task in filtered_schedule)))
            
            # Initialize variables first
            threed_data = []
            project_start = None
            project_end = None
            project_duration = 0
            show_3d_viz = False
            
            # Add option to toggle 3D visualization
            show_3d = st.checkbox("Show 3D Visualization", value=False, 
                               help="Enable/disable the 3D visualization to improve performance")
            
            if not show_3d:
                st.info("3D visualization is disabled to improve performance. Check the box above to enable it.")
            else:
                # Add a loading indicator
                with st.spinner("Preparing 3D visualization..."):
                    # Normalize dates once before processing
                    normalized_schedule = []
                    for task in filtered_schedule:
                        task_copy = task.copy()
                        
                        # Convert string dates to date objects
                        if isinstance(task_copy['start_date'], str):
                            task_copy['start_date'] = datetime.strptime(task_copy['start_date'], '%Y-%m-%d').date()
                        elif isinstance(task_copy['start_date'], datetime):
                            task_copy['start_date'] = task_copy['start_date'].date()
                        
                        if isinstance(task_copy['end_date'], str):
                            task_copy['end_date'] = datetime.strptime(task_copy['end_date'], '%Y-%m-%d').date()
                        elif isinstance(task_copy['end_date'], datetime):
                            task_copy['end_date'] = task_copy['end_date'].date()
                            
                        normalized_schedule.append(task_copy)
                    
                    # Calculate the project timeline parameters once
                    all_start_dates = [task['start_date'] for task in normalized_schedule]  # Already normalized
                    all_end_dates = [task['end_date'] for task in normalized_schedule]  # Already normalized
                    
                    project_start = min(all_start_dates)
                    project_end = max(all_end_dates)
                    project_duration = max(1, (project_end - project_start).days)
                    
                    # Add message for project timeline
                    st.write(f"Project timeline: {project_start} to {project_end} ({project_duration} days)")
                    
                    # Group tasks by phase for more efficient processing
                    phase_groups = {}
                    for phase in phases:
                        phase_groups[phase] = []
                        
                    # Pre-sort tasks into phases
                    for task in normalized_schedule:
                        phase_groups[task['phase']].append(task)
                    
                    # Process each phase group
                    for phase_idx, phase in enumerate(phases):
                        # Get and sort tasks for this phase
                        phase_tasks = sorted(phase_groups[phase], key=lambda x: x['start_date'])
                        
                        # Process only a limited number of tasks if there are too many
                        max_tasks_per_phase = 25  # Limit for performance
                        if len(phase_tasks) > max_tasks_per_phase:
                            st.warning(f"Phase '{phase}' has {len(phase_tasks)} tasks. Showing only {max_tasks_per_phase} for performance reasons.")
                            # Choose tasks distributed across the timeline
                            step = len(phase_tasks) // max_tasks_per_phase
                            phase_tasks = [phase_tasks[i] for i in range(0, len(phase_tasks), step)][:max_tasks_per_phase]
                        
                        # For each task in this phase
                        for task_idx, task in enumerate(phase_tasks):
                            # Use normalized date objects
                            start = task['start_date']
                            end = task['end_date']
                            duration = (end - start).days
                            
                            # Use manual completion percentage if available
                            if hasattr(st.session_state, 'using_manual_completion') and st.session_state.using_manual_completion and 'manual_completion' in task:
                                completion = task['manual_completion']
                            else:
                                # Calculate completion based on dates
                                days_passed = (today - start).days
                                
                                if days_passed < 0:  # Task hasn't started yet
                                    completion = 0
                                elif days_passed >= duration:  # Task is complete
                                    completion = 100
                                else:  # Task is in progress
                                    completion = min(100, max(0, int((days_passed / duration) * 100)))
                            
                            # Simplified color calculation
                            if task.get('critical_path', False):
                                # Red to green for critical path
                                color = f'rgb({255-int(2.55*completion)},{int(2.55*completion)},0)'
                            else:
                                # Blue-based for regular tasks
                                color = f'rgb({50+int(completion)},{100+int(1.5*completion)},{200+int(0.55*completion)})'
                            
                            # Add to the 3D dataset with simplified calculations
                            threed_data.append({
                                'task': task['task_name'],
                                'phase': phase,
                                'resource': task.get('responsible_party', 'Unassigned'),
                                'start': start.strftime('%Y-%m-%d'),
                                'end': end.strftime('%Y-%m-%d'),
                                'duration': duration,
                                'x': (start - project_start).days / project_duration,
                                'y': phase_idx,
                                'z': max(0.02, duration / project_duration) / 2,  # Center point
                                'width': max(0.02, duration / project_duration),  # Duration
                                'height': 1.5 if task.get('critical_path', False) else 1.0,
                                'completion': completion,
                                'color': color,
                                'critical': task.get('critical_path', False)
                            })
                    
                    # Flag that 3D viz is ready
                    show_3d_viz = True
            
            # Only create and display the visualization if enabled and data exists
            if show_3d and threed_data and show_3d_viz:
                # Convert to DataFrame for easier manipulation
                df_3d = pd.DataFrame(threed_data)
                
                # Create 3D bar chart
                fig = go.Figure()
                
                # Process each row in the dataframe
                for _, row in df_3d.iterrows():
                    # Create box shape with 3D effect
                    fig.add_trace(go.Scatter3d(
                        x=[row['x'], row['x'] + row['width'], row['x'] + row['width'], row['x'], row['x'],  # Base x positions
                           row['x'], row['x'] + row['width'], row['x'] + row['width'], row['x']],  # Top x positions
                        y=[row['y'], row['y'], row['y'], row['y'], row['y'],  # Base y positions
                           row['y'] + row['height'], row['y'] + row['height'], row['y'] + row['height'], row['y'] + row['height']],  # Top y positions
                        z=[0, 0, 0, 0, 0,  # Base z positions are all 0
                           row['height'], row['height'], row['height'], row['height']],  # Top z positions
                        mode='lines',
                        line=dict(color=row['color'], width=10),
                        hoverinfo='text',
                        hovertext=f"<b>{row['task']}</b><br>" +
                                 f"Phase: {row['phase']}<br>" +
                                 f"Resource: {row['resource']}<br>" +
                                 f"Start: {row['start']}<br>" +
                                 f"End: {row['end']}<br>" +
                                 f"Duration: {row['duration']} days<br>" +
                                 f"Completion: {row['completion']}%<br>" +
                                 f"Critical Path: {'Yes' if row['critical'] else 'No'}",
                        name=row['task'],
                        showlegend=False
                    ))
                    
                    # Add a colored surface on top to create a more solid appearance
                    fig.add_trace(go.Surface(
                        x=[[row['x'], row['x'] + row['width']], 
                           [row['x'], row['x'] + row['width']]],
                        y=[[row['y'], row['y']], 
                           [row['y'], row['y']]],
                        z=[[row['height'], row['height']], 
                           [row['height'], row['height']]],
                        colorscale=[[0, row['color']], [1, row['color']]],
                        showscale=False,
                        hoverinfo='skip',
                        showlegend=False,
                        opacity=0.95
                    ))
                    
                    # Add text label for task name
                    fig.add_trace(go.Scatter3d(
                        x=[row['x'] + row['width']/2],
                        y=[row['y'] + row['height']/2],
                        z=[row['height'] + 0.05],
                        mode='text',
                        text=f"{row['task']}<br>{row['completion']}%",
                        hoverinfo='skip',
                        textfont=dict(
                            color='black',
                            size=12
                        ),
                        showlegend=False
                    ))
                
                # Add a ground plane for better depth perception
                x_min, x_max = 0, 1
                y_min, y_max = 0, len(phases)
                grid_x, grid_y = np.meshgrid(np.linspace(x_min, x_max, 10), np.linspace(y_min, y_max, 10))
                grid_z = np.zeros_like(grid_x)
                
                fig.add_trace(go.Surface(
                    x=grid_x,
                    y=grid_y,
                    z=grid_z,
                    colorscale=[[0, 'rgba(230, 230, 230, 0.5)'], [1, 'rgba(200, 200, 200, 0.5)']],
                    showscale=False,
                    hoverinfo='skip'
                ))
                
                # Add phase labels on Y-axis
                for i, phase in enumerate(phases):
                    fig.add_trace(go.Scatter3d(
                        x=[0],
                        y=[i + 0.5],
                        z=[0],
                        mode='text',
                        text=phase,
                        textposition="middle left",
                        textfont=dict(
                            color='black',
                            size=14,
                            family='Arial, sans-serif'
                        ),
                        showlegend=False
                    ))
                
                # Add timeline markers on X-axis (convert normalized positions back to dates)
                date_markers = []
                project_duration_days = (project_end - project_start).days
                
                # Generate date markers at regular intervals
                for i in range(0, 11):  # 0 to 10 points
                    position = i / 10
                    days_from_start = int(position * project_duration_days)
                    marker_date = project_start + timedelta(days=days_from_start)
                    date_markers.append((position, marker_date.strftime("%Y-%m-%d")))
                
                # Add date labels
                for pos, date_label in date_markers:
                    fig.add_trace(go.Scatter3d(
                        x=[pos],
                        y=[-0.5],  # Just below the grid
                        z=[0],
                        mode='text',
                        text=date_label,
                        textposition="middle center",
                        textfont=dict(
                            color='black',
                            size=10,
                            family='Arial, sans-serif'
                        ),
                        showlegend=False
                    ))
                    
                    # Add vertical lines for date markers
                    fig.add_trace(go.Scatter3d(
                        x=[pos, pos],
                        y=[0, len(phases)],
                        z=[0, 0],
                        mode='lines',
                        line=dict(
                            color='rgba(150, 150, 150, 0.3)',
                            width=2,
                            dash='dash'
                        ),
                        showlegend=False
                    ))
                
                # Add today marker
                today_normalized = (today - project_start).days / max(1, project_duration_days)
                if 0 <= today_normalized <= 1:  # Check if today is within project timeframe
                    fig.add_trace(go.Scatter3d(
                        x=[today_normalized, today_normalized],
                        y=[0, len(phases)],
                        z=[0, 3],  # Make it tall enough to be visible
                        mode='lines',
                        line=dict(
                            color='rgba(0, 200, 0, 0.8)',
                            width=5
                        ),
                        name="Today",
                        showlegend=True
                    ))
                    
                    fig.add_trace(go.Scatter3d(
                        x=[today_normalized],
                        y=[len(phases) + 0.5],
                        z=[1.5],
                        mode='text',
                        text="TODAY",
                        textposition="top center",
                        textfont=dict(
                            color='green',
                            size=16,
                            family='Arial Black, Arial Bold, Arial'
                        ),
                        showlegend=False
                    ))
                
                # Add critical path indicator for legend
                fig.add_trace(go.Scatter3d(
                    x=[None], y=[None], z=[None],
                    mode='markers',
                    marker=dict(size=10, color='red'),
                    name='Critical Path Tasks',
                    showlegend=True
                ))
                
                # Add regular task indicator for legend
                fig.add_trace(go.Scatter3d(
                    x=[None], y=[None], z=[None],
                    mode='markers',
                    marker=dict(size=10, color='rgb(0, 180, 230)'),
                    name='Regular Tasks',
                    showlegend=True
                ))
                
                # Layout configuration
                camera = dict(
                    eye=dict(x=1.5, y=-1.5, z=1.25),
                    up=dict(x=0, y=0, z=1)
                )
                
                fig.update_layout(
                    title={
                        'text': '3D Construction Project Timeline',
                        'font': {'size': 28, 'color': '#333', 'family': 'Arial Black, Arial Bold, Arial'},
                        'x': 0.5,
                        'y': 0.95,
                        'xanchor': 'center'
                    },
                    width=1000,
                    height=800,
                    scene=dict(
                        xaxis=dict(
                            title='Project Timeline',
                            showbackground=False,
                            showgrid=False,
                            showticklabels=False,
                            zeroline=False
                        ),
                        yaxis=dict(
                            title='Construction Phases',
                            showbackground=False,
                            showgrid=False,
                            showticklabels=False,
                            zeroline=False
                        ),
                        zaxis=dict(
                            title='Task Importance',
                            showbackground=False,
                            showgrid=False,
                            showticklabels=False,
                            zeroline=False
                        ),
                        aspectratio=dict(x=1.5, y=1, z=0.5),
                        camera=camera
                    ),
                    paper_bgcolor='rgba(250, 250, 250, 0.9)',
                    legend=dict(
                        font=dict(size=14),
                        itemsizing='constant',
                        bgcolor='rgba(255, 255, 255, 0.8)',
                        bordercolor='rgba(0, 0, 0, 0.2)',
                        borderwidth=1
                    ),
                    margin=dict(l=0, r=0, t=50, b=0),
                )
                
                # Add interactive annotation
                st.markdown("""
                <div style="background-color:rgba(0,120,200,0.1); padding:10px; border-radius:5px; 
                            text-align:center; border:1px solid rgba(0,120,200,0.2); margin-bottom:10px;">
                    <p style="margin:0; color:#333;">
                        <b>Interactive 3D View:</b> Click and drag to rotate | Scroll to zoom | Double-click to reset view
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the 3D visualization
                st.plotly_chart(fig, use_container_width=True)
            
            # Add a 2D timeline for reference - make it optional for better performance
            st.subheader("2D Timeline Reference")
            
            # Option to show/hide 2D timeline
            show_2d = st.checkbox("Show 2D Timeline", value=True,
                             help="Enable/disable the 2D timeline to improve performance")
            
            # Initialize timeline_df as None so we can check if it was created
            timeline_df = None
            
            if not show_2d:
                st.info("2D timeline is disabled to improve performance. Check the box above to enable it.")
            elif not show_3d or 'threed_data' not in locals():
                st.info("Enable the 3D visualization above to view the 2D timeline.")
            else:
                # Use simplified 2D timeline for better performance
                with st.spinner("Preparing 2D timeline..."):
                    # Convert data to Gantt chart format more efficiently
                    gantt_data = []
                    
                    # Safely access threed_data with error handling
                    try:
                        # Limit number of tasks for performance
                        max_tasks = 50
                        if len(threed_data) > max_tasks:
                            st.info(f"Showing {max_tasks} out of {len(threed_data)} tasks for better performance.")
                            # Sample tasks evenly across the dataset
                            indices = np.linspace(0, len(threed_data) - 1, max_tasks, dtype=int)
                            tasks_to_show = [threed_data[i] for i in indices]
                        else:
                            tasks_to_show = threed_data
                        
                        # Directly use the completion values from 3D data to avoid recalculation
                        for task in tasks_to_show:
                            gantt_data.append({
                                'Task': task['task'],
                                'Start': task['start'],
                                'Finish': task['end'],
                                'Resource': task['resource'],
                                'Phase': task['phase'],
                                'Duration': task['duration'],
                                'Critical': 'Yes' if task['critical'] else 'No',
                                'Completion': task['completion']  # Already calculated in 3D visualization
                            })
                        
                        # Create the timeline DataFrame directly with all data
                        if gantt_data:
                            timeline_df = pd.DataFrame(gantt_data)
                    except Exception as e:
                        st.warning(f"Could not create 2D timeline: {e}")
                        timeline_df = None
            
            if show_2d and 'threed_data' in locals() and timeline_df is not None and len(timeline_df) > 0:
                # Create a simplified 2D timeline
                fig2d = px.timeline(
                    timeline_df, 
                    x_start='Start', 
                    x_end='Finish', 
                    y='Task', 
                    color='Phase',
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                
                # Add today marker using a shape instead of vline to avoid type error
                fig2d.add_shape(
                    type="line",
                    x0=today,
                    x1=today,
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(
                        color="green",
                        width=2,
                        dash="dash",
                    )
                )
                
                # Add Today label
                fig2d.add_annotation(
                    x=today,
                    y=1.05,
                    yref="paper",
                    text="Today",
                    showarrow=False,
                    font=dict(
                        color="green",
                        size=12,
                        family="Arial, sans-serif"
                    )
                )
                
                # Simplify layout
                fig2d.update_layout(
                    height=400,
                    xaxis_title="Timeline",
                    yaxis_title="Tasks",
                    legend_title="Construction Phases",
                    font=dict(family='Arial', size=12),
                    uniformtext_minsize=10,
                    uniformtext_mode='hide',
                    plot_bgcolor='rgba(240, 240, 240, 0.8)',  # Light gray background
                )
                
                # Make the chart more readable
                fig2d.update_traces(
                    marker_line_width=2,
                    marker_line_color="white",
                    opacity=0.8
                )
                
                # Display the 2D timeline
                st.plotly_chart(fig2d, use_container_width=True)
            
            # Add a completion meter
            st.subheader("Project Completion Meter")
            
            # Calculate overall project completion
            all_tasks = st.session_state.schedule
            all_durations = [
                (get_date(task['end_date']) - get_date(task['start_date'])).days 
                for task in all_tasks
            ]
            total_duration_days = sum(all_durations)
            
            # Calculate weighted completion for each task
            weighted_completions = []
            for task in all_tasks:
                start = get_date(task['start_date'])
                end = get_date(task['end_date'])
                duration = (end - start).days
                
                # Task weight based on duration proportion
                task_weight = duration / total_duration_days if total_duration_days > 0 else 0
                
                # Use manual completion percentage if available
                if hasattr(st.session_state, 'using_manual_completion') and st.session_state.using_manual_completion and 'manual_completion' in task:
                    task_completion = task['manual_completion']
                else:
                    # Calculate completion based on dates
                    if today < start:
                        task_completion = 0
                    elif today > end:
                        task_completion = 100
                    else:
                        days_passed = (today - start).days
                        task_completion = min(100, max(0, int((days_passed / duration) * 100))) if duration > 0 else 100
                
                weighted_completions.append(task_completion * task_weight)
            
            # Overall project completion
            overall_completion = sum(weighted_completions)
            
            # Create a more detailed progress visualization
            # First, create a colorful progress bar
            if overall_completion < 30:
                bar_color = "rgba(255,0,0,0.8)"  # Red for early stages
            elif overall_completion < 70:
                bar_color = "rgba(255,165,0,0.8)"  # Orange for middle stages
            else:
                bar_color = "rgba(0,128,0,0.8)"  # Green for late stages
                
            # Custom CSS for a more stylized progress bar
            st.markdown(
                f"""
                <style>
                    .completion-bar {{
                        width: 100%;
                        background-color: #f0f0f0;
                        border-radius: 10px;
                        margin-bottom: 20px;
                        height: 30px;
                        overflow: hidden;
                        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
                    }}
                    .completion-fill {{
                        height: 100%;
                        width: {overall_completion}%;
                        background-color: {bar_color};
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        text-shadow: 1px 1px 1px rgba(0,0,0,0.3);
                        transition: width 0.5s ease-in-out;
                    }}
                </style>
                <div class="completion-bar">
                    <div class="completion-fill">{overall_completion:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display completion percentage with a large, colorful style
            completion_col1, completion_col2 = st.columns([1, 3])
            with completion_col1:
                st.markdown(
                    f"""
                    <div style="background-color:rgba(0,120,200,0.1); padding:20px; border-radius:10px; 
                               text-align:center; border:2px solid rgba(0,120,200,0.2);">
                        <h1 style="margin:0; color:#0078C8; font-size:3rem;">{overall_completion:.1f}%</h1>
                        <p style="margin:0; color:#333; font-size:1.2rem;">Project Completion</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with completion_col2:
                # Add remaining project stats in a modern card layout
                # First normalize date objects for proper comparison
                normalized_tasks = []
                for task in all_tasks:
                    task_copy = task.copy()
                    if isinstance(task_copy['start_date'], str):
                        task_copy['start_date'] = datetime.strptime(task_copy['start_date'], '%Y-%m-%d').date()
                    elif isinstance(task_copy['start_date'], datetime):
                        task_copy['start_date'] = task_copy['start_date'].date()
                    
                    if isinstance(task_copy['end_date'], str):
                        task_copy['end_date'] = datetime.strptime(task_copy['end_date'], '%Y-%m-%d').date()
                    elif isinstance(task_copy['end_date'], datetime):
                        task_copy['end_date'] = task_copy['end_date'].date()
                    
                    normalized_tasks.append(task_copy)
                
                # Calculate remaining days using normalized dates
                # Get the latest end date (project completion)
                final_end_date = max(task['end_date'] for task in normalized_tasks)
                
                # Calculate remaining days until project completion
                # Ensure both dates are proper date objects for comparison
                if isinstance(final_end_date, datetime):
                    final_end_date = final_end_date.date()
                if isinstance(today, datetime):
                    today = today.date()
                
                # Ensure both are date objects
                if isinstance(final_end_date, date) and isinstance(today, date):
                    remaining_days = (final_end_date - today).days if final_end_date > today else 0
                else:
                    # Handle error case
                    st.error(f"Date conversion issue - final_end_date: {type(final_end_date)}, today: {type(today)}")
                    remaining_days = 0
                
                # Remove debug info and add a phase completion chart instead
                # Calculate phase completion percentages
                phase_completion_data = []
                phases = sorted(list(set(task['phase'] for task in normalized_tasks)))
                
                # Debug information to help diagnose
                st.write(f"Number of tasks found: {len(normalized_tasks)}")
                st.write(f"Today's date for calculations: {today}")
                
                for phase in phases:
                    phase_tasks = [task for task in normalized_tasks if task['phase'] == phase]
                    
                    # Calculate completion by weighted task completions
                    total_phase_duration = sum((task['end_date'] - task['start_date']).days for task in phase_tasks)
                    
                    if total_phase_duration <= 0:
                        phase_completion = 100  # Avoid division by zero
                    else:
                        weighted_sum = 0
                        for task in phase_tasks:
                            task_duration = (task['end_date'] - task['start_date']).days
                            weight = task_duration / total_phase_duration if total_phase_duration > 0 else 0
                            
                            # Use manual completion if available
                            if hasattr(st.session_state, 'using_manual_completion') and st.session_state.using_manual_completion and 'manual_completion' in task:
                                task_completion = task['manual_completion']
                            else:
                                # Calculate completion based on dates
                                if today < task['start_date']:
                                    task_completion = 0
                                elif today > task['end_date']:
                                    task_completion = 100
                                else:
                                    task_days = max(1, (task['end_date'] - task['start_date']).days)
                                    days_passed = (today - task['start_date']).days
                                    task_completion = min(100, max(0, int((days_passed / task_days) * 100)))
                            
                            weighted_sum += task_completion * weight
                        
                        phase_completion = round(weighted_sum, 1)
                    
                    phase_completion_data.append({
                        'Phase': phase,
                        'Completion': phase_completion
                    })
                
                # Create a DataFrame for the phase completion chart
                phase_completion_df = pd.DataFrame(phase_completion_data)
                
                # Create a completion percentage by phase chart
                fig = px.bar(
                    phase_completion_df,
                    x='Phase',
                    y='Completion',
                    title='Completion Percentage by Construction Phase',
                    text='Completion',
                    color='Completion',
                    color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
                    range_color=[0, 100]
                )
                
                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    marker_line_width=1.5,
                    marker_line_color='white'
                )
                
                fig.update_layout(
                    yaxis_range=[0, 105],  # Set y-axis range from 0 to 105 to make room for labels
                    yaxis_title='Completion Percentage',
                    xaxis_title='Construction Phase',
                    coloraxis_showscale=False,
                    font=dict(family="Arial", size=12),
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                
                # Display the chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Now calculate task counts using normalized dates
                # Make sure we're comparing date objects of the same type
                today_date = today
                if isinstance(today, datetime):
                    today_date = today.date()
                
                # Display task counts with debug information
                st.write(f"Calculating task counts based on today ({today_date})")
                
                # Count tasks based on manual completion percentages
                completed_tasks = 0
                in_progress_with_completion = 0

                # Check if we're using manual completion mode
                if hasattr(st.session_state, 'using_manual_completion') and st.session_state.using_manual_completion:
                    # Count tasks that are marked as 100% complete
                    for task in normalized_tasks:
                        task_id = task.get('id', task.get('task_name', ''))
                        if 'manual_completion' in task and task['manual_completion'] == 100:
                            completed_tasks += 1
                        elif 'manual_completion' in task and task['manual_completion'] > 0:
                            in_progress_with_completion += 1
                else:
                    # Traditional date-based counting
                    for task in normalized_tasks:
                        end_date = task['end_date']
                        if isinstance(end_date, datetime):
                            end_date = end_date.date()
                        if end_date < today_date:
                            completed_tasks += 1
                
                # Count in-progress tasks
                in_progress_tasks = 0
                
                # If using manual completion, count tasks with partial completion percentages
                if hasattr(st.session_state, 'using_manual_completion') and st.session_state.using_manual_completion:
                    # Use the previously calculated in_progress_with_completion
                    in_progress_tasks = in_progress_with_completion
                    
                    # Also count tasks with no completion value yet as in-progress
                    # Get total task count
                    total_tasks = len(normalized_tasks)
                    not_started = total_tasks - completed_tasks - in_progress_with_completion
                    future_tasks = not_started  # will be updated later
                else:
                    # Traditional date-based counting - today is between start and end dates
                    for task in normalized_tasks:
                        start_date = task['start_date']
                        end_date = task['end_date']
                        if isinstance(start_date, datetime):
                            start_date = start_date.date()
                        if isinstance(end_date, datetime):
                            end_date = end_date.date()
                        if start_date <= today_date <= end_date:
                            in_progress_tasks += 1
                
                # Count future tasks
                if hasattr(st.session_state, 'using_manual_completion') and st.session_state.using_manual_completion:
                    # In manual mode, we already calculated future_tasks as tasks with 0% completion
                    # The value was set in the in-progress tasks section
                    pass  # Don't recalculate, use the value from before
                else:
                    # Traditional date-based counting - start date is after today
                    future_tasks = 0
                    for task in normalized_tasks:
                        start_date = task['start_date']
                        if isinstance(start_date, datetime):
                            start_date = start_date.date()
                        if start_date > today_date:
                            future_tasks += 1
                
                # Show counts summary for verification
                st.write(f"Task counts: {completed_tasks} completed, {in_progress_tasks} in progress, {future_tasks} upcoming")
                
                st.markdown(
                    f"""
                    <div style="display:flex; flex-wrap:wrap; gap:10px; height:100%;">
                        <div style="flex:1; min-width:150px; background-color:rgba(0,180,0,0.1); padding:15px; border-radius:10px; 
                                  text-align:center; border:2px solid rgba(0,180,0,0.2);">
                            <h3 style="margin:0; color:#00A000; font-size:1.8rem;">{completed_tasks}</h3>
                            <p style="margin:0; color:#333;">Completed Tasks</p>
                        </div>
                        <div style="flex:1; min-width:150px; background-color:rgba(255,180,0,0.1); padding:15px; border-radius:10px; 
                                  text-align:center; border:2px solid rgba(255,180,0,0.2);">
                            <h3 style="margin:0; color:#FFA000; font-size:1.8rem;">{in_progress_tasks}</h3>
                            <p style="margin:0; color:#333;">In Progress</p>
                        </div>
                        <div style="flex:1; min-width:150px; background-color:rgba(200,0,0,0.1); padding:15px; border-radius:10px; 
                                  text-align:center; border:2px solid rgba(200,0,0,0.2);">
                            <h3 style="margin:0; color:#C00000; font-size:1.8rem;">{future_tasks}</h3>
                            <p style="margin:0; color:#333;">Upcoming Tasks</p>
                        </div>
                        <div style="flex:1; min-width:150px; background-color:rgba(100,100,100,0.1); padding:15px; border-radius:10px; 
                                  text-align:center; border:2px solid rgba(100,100,100,0.2);">
                            <h3 style="margin:0; color:#555; font-size:1.8rem;">{remaining_days}</h3>
                            <p style="margin:0; color:#333;">Days Remaining</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Display metrics
        # Calculate metrics based on the filtered schedule view
        if filtered_schedule:
            # Use the currently selected date range for metrics
            filtered_earliest_start = min(get_date(task['start_date']) for task in filtered_schedule)
            filtered_latest_end = max(get_date(task['end_date']) for task in filtered_schedule)
            filtered_duration = (filtered_latest_end - filtered_earliest_start).days
            
            # Get the overall project dates for comparison
            overall_earliest_start = min(get_date(task['start_date']) for task in st.session_state.schedule)
            overall_latest_end = max(get_date(task['end_date']) for task in st.session_state.schedule)
            overall_duration = (overall_latest_end - overall_earliest_start).days
            
            # Display filtered view metrics
            col1, col2, col3 = st.columns(3)
            col1.metric(
                "Selected View Start Date", 
                filtered_earliest_start.strftime("%Y-%m-%d"),
                delta=f"{(filtered_earliest_start - overall_earliest_start).days} days from project start" if filtered_earliest_start > overall_earliest_start else "Project start"
            )
            
            # Fix end date display with proper formatting and date handling
            col2.metric(
                "Selected View End Date", 
                filtered_latest_end.strftime("%Y-%m-%d"),
                delta=f"{(overall_latest_end - filtered_latest_end).days} days before project end" if filtered_latest_end < overall_latest_end else "Project end"
            )
            
            col3.metric(
                "Selected Duration", 
                f"{filtered_duration} days",
                delta=f"{round(filtered_duration/overall_duration*100)}% of total" if filtered_duration != overall_duration else "Full project"
            )
            
            # Add a second row with overall project metrics
            st.write("### Overall Project Timeline")
            overall_col1, overall_col2, overall_col3 = st.columns(3)
            overall_col1.metric("Project Start Date", overall_earliest_start.strftime("%Y-%m-%d"))
            overall_col2.metric("Project End Date", overall_latest_end.strftime("%Y-%m-%d"))
            overall_col3.metric("Total Project Duration", f"{overall_duration} days")
        else:
            # Fallback if filtered schedule is empty
            earliest_start = min(get_date(task['start_date']) for task in st.session_state.schedule)
            latest_end = max(get_date(task['end_date']) for task in st.session_state.schedule)
            project_duration = (latest_end - earliest_start).days
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Project Start Date", earliest_start.strftime("%Y-%m-%d"))
            col2.metric("Project End Date", latest_end.strftime("%Y-%m-%d"))
            col3.metric("Project Duration", f"{project_duration} days")
        
        # Display task distribution by phase
        st.subheader("Tasks by Construction Phase")
        phase_counts = {}
        for task in st.session_state.schedule:
            if task['phase'] not in phase_counts:
                phase_counts[task['phase']] = 0
            phase_counts[task['phase']] += 1
        
        phase_df = pd.DataFrame({
            'Phase': list(phase_counts.keys()),
            'Number of Tasks': list(phase_counts.values())
        })
        
        # Simplified tasks by phase bar chart
        fig = px.bar(
            phase_df, 
            x='Phase', 
            y='Number of Tasks', 
            title='Tasks Distribution by Construction Phase',
            text='Number of Tasks',
            color_discrete_sequence=['#636efa']  # Single blue color
        )
        
        fig.update_layout(
            xaxis_title="Construction Phase",
            yaxis_title="Number of Tasks",
            font=dict(family="Arial", size=14),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )
        
        # Add value labels on top of bars
        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add a new visualization - Project Timeline Bar Chart
        st.subheader("Project Timeline Progress")
        
        # Create a timeline summary by phase
        timeline_data = []
        phases = sorted(list(set(task['phase'] for task in st.session_state.schedule)))
        
        for phase in phases:
            phase_tasks = [task for task in st.session_state.schedule if task['phase'] == phase]
            earliest_start = min(get_date(task['start_date']) for task in phase_tasks)
            latest_end = max(get_date(task['end_date']) for task in phase_tasks)
            duration = (latest_end - earliest_start).days
            
            # Calculate completion percentage based on task completions
            # If we have manual completion values, use weighted average of those tasks
            if hasattr(st.session_state, 'using_manual_completion') and st.session_state.using_manual_completion:
                # Calculate weighted completion for phase based on manual task completions
                total_phase_duration = sum((get_date(task['end_date']) - get_date(task['start_date'])).days for task in phase_tasks)
                
                if total_phase_duration <= 0:
                    completion = 100  # Avoid division by zero
                else:
                    weighted_sum = 0
                    for task in phase_tasks:
                        task_duration = (get_date(task['end_date']) - get_date(task['start_date'])).days
                        weight = task_duration / total_phase_duration
                        if 'manual_completion' in task:
                            weighted_sum += task['manual_completion'] * weight
                        else:
                            # If a task doesn't have manual completion, calculate it
                            today = datetime.now().date()
                            start = get_date(task['start_date'])
                            end = get_date(task['end_date'])
                            if today < start:
                                task_completion = 0
                            elif today > end:
                                task_completion = 100
                            else:
                                task_days = (end - start).days
                                if task_days <= 0:
                                    task_completion = 100
                                else:
                                    days_passed = (today - start).days
                                    task_completion = min(100, max(0, int((days_passed / task_days) * 100)))
                            weighted_sum += task_completion * weight
                    
                    completion = int(weighted_sum)
            else:
                # Traditional calculation based on today's date
                today = datetime.now().date()
                if today < earliest_start:
                    completion = 0
                elif today > latest_end:
                    completion = 100
                else:
                    days_passed = (today - earliest_start).days
                    completion = min(100, max(0, int((days_passed / duration) * 100)))
            
            timeline_data.append({
                'Phase': phase,
                'Start Date': earliest_start,
                'End Date': latest_end,
                'Duration (days)': duration,
                'Completion': completion
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create a horizontal bar chart showing phase durations with completion indicators
        # Simplified project timeline progress chart
        fig = px.bar(
            timeline_df, 
            y='Phase', 
            x='Duration (days)', 
            color_discrete_sequence=['#5388D8'],  # Single uniform color
            labels={'Duration (days)': 'Duration (days)', 'Phase': 'Construction Phase'},
            title='Construction Phases Timeline',
            text='Completion',  # Keep completion as text inside bars
            hover_data=['Start Date', 'End Date', 'Duration (days)']
        )
        
        fig.update_layout(
            height=500,
            yaxis={'categoryorder':'array', 'categoryarray': list(reversed(phases))},
            font=dict(family="Arial", size=14),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            # Add a vertical line for today's date
            shapes=[dict(
                type='line',
                x0=0,
                x1=max(timeline_df['Duration (days)']),
                y0=-0.5,
                y1=len(timeline_df) - 0.5,
                yref='y',
                line=dict(color='rgba(0,0,0,0.3)', width=2, dash='dot')
            )]
        )
        
        # Add value labels showing completion percentage
        fig.update_traces(
            texttemplate='%{text}%',
            textposition='inside',
            insidetextanchor='middle',
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display critical path
        st.subheader("Critical Path")
        critical_tasks = [task for task in st.session_state.schedule if task.get('critical_path', False)]
        if critical_tasks:
            critical_df = pd.DataFrame(critical_tasks)
            st.dataframe(critical_df, use_container_width=True)
            
            # Create a timeline for critical path
            fig = px.timeline(critical_df, x_start='start_date', x_end='end_date', y='task_name',
                             title='Critical Path Timeline')
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No critical path identified for this project.")

# Tab 4: Export Results
with tab4:
    st.header("Export Results")
    
    if st.session_state.materials is None or st.session_state.schedule is None:
        st.info("Please upload and process a blueprint first.")
    else:
        # Add settings for currency and unit conversion for exports
        st.subheader("Export Settings")
        
        settings_col1, settings_col2 = st.columns(2)
        
        # Currency selection
        with settings_col1:
            # Currency conversion rates (USD to other currencies)
            currency_rates = {
                "USD": 1.0,
                "INR": 83.5,  # Indian Rupee
                "EUR": 0.92,  # Euro
                "GBP": 0.79,  # British Pound
                "JPY": 151.2, # Japanese Yen
                "CNY": 7.22,  # Chinese Yuan
                "AUD": 1.50,  # Australian Dollar
                "CAD": 1.36,  # Canadian Dollar
            }
            
            currency_symbols = {
                "USD": "$",
                "INR": "₹",
                "EUR": "€",
                "GBP": "£",
                "JPY": "¥",
                "CNY": "¥",
                "AUD": "A$",
                "CAD": "C$",
            }
            
            export_currency = st.selectbox(
                "Select Currency for Export:", 
                options=list(currency_rates.keys()),
                format_func=lambda x: f"{x} ({currency_symbols[x]})",
                index=1,  # Default to INR
                key="export_currency"
            )
            
            # Store the conversion rate
            export_rate = currency_rates[export_currency]
            export_symbol = currency_symbols[export_currency]
            
        # Unit conversion selection
        with settings_col2:
            # Unit conversion options and rates
            unit_conversions = {
                "No Conversion": {
                    "cubic yards": (1.0, "cubic yards"),
                    "sq ft": (1.0, "sq ft"),
                    "linear feet": (1.0, "linear feet"),
                    "pieces": (1.0, "pieces"),
                    "tons": (1.0, "tons"),
                    "gallons": (1.0, "gallons")
                },
                "Metric": {
                    "cubic yards": (0.764555, "cubic meters"),
                    "sq ft": (0.092903, "sq meters"),
                    "linear feet": (0.3048, "meters"),
                    "pieces": (1.0, "pieces"),
                    "tons": (0.907185, "tonnes"),
                    "gallons": (3.78541, "liters")
                },
                "Imperial (UK)": {
                    "cubic yards": (0.764555, "cubic yards"),
                    "sq ft": (0.092903, "sq feet"),
                    "linear feet": (0.3048, "feet"),
                    "pieces": (1.0, "pieces"),
                    "tons": (1.0, "tons"),
                    "gallons": (0.832674, "imp. gallons")
                }
            }
            
            export_units = st.selectbox(
                "Select Unit System for Export:",
                options=list(unit_conversions.keys()),
                index=1,  # Default to Metric
                key="export_units"
            )
            
            # Store the unit conversion dictionary
            export_converters = unit_conversions[export_units]
        
        # Function to convert material values based on settings
        def convert_export_material(item):
            # Copy the original item
            converted = item.copy()
            
            # Apply currency conversion to cost
            if 'cost' in item:
                converted['cost'] = item['cost'] * export_rate
            
            # Apply currency conversion to cost_per_unit if it exists
            if 'cost_per_unit' in item:
                converted['cost_per_unit'] = item['cost_per_unit'] * export_rate
            else:
                # Calculate cost per unit if not present
                if 'cost' in item and 'quantity' in item and item['quantity'] > 0:
                    converted['cost_per_unit'] = item['cost'] / item['quantity']
                else:
                    converted['cost_per_unit'] = 0
            
            # Apply unit conversion if needed
            if 'unit' in item:
                original_unit = item['unit']
                if original_unit in export_converters:
                    factor, new_unit = export_converters[original_unit]
                    if 'quantity' in item:
                        converted['quantity'] = item['quantity'] * factor
                    converted['unit'] = new_unit
                    # Adjust cost per unit based on the new unit
                    if 'cost_per_unit' in converted and factor > 0:
                        converted['cost_per_unit'] = converted['cost_per_unit'] / factor
            
            # Format cost values for display
            if 'cost' in converted:
                converted['display_cost'] = f"{export_symbol}{converted['cost']:,.2f}"
            if 'cost_per_unit' in converted:
                converted['display_cost_per_unit'] = f"{export_symbol}{converted['cost_per_unit']:,.2f}"
            
            return converted
            
        # Convert all materials based on selected currency and units
        export_materials = [convert_export_material(item) for item in st.session_state.materials]
        
        # Add a note about conversions
        st.info(f"💡 All exports will use {export_currency} ({export_symbol}) currency and {export_units} measurement system.")
        
        st.subheader("Export Options")
        
        # Generate CSV data for materials with conversions applied
        materials_csv = io.StringIO()
        materials_df = pd.DataFrame(export_materials)
        materials_df.to_csv(materials_csv, index=False)
        
        # Generate CSV data for schedule
        schedule_csv = io.StringIO()
        schedule_df = pd.DataFrame(st.session_state.schedule)
        schedule_df.to_csv(schedule_csv, index=False)
        
        col1, col2 = st.columns(2)
        
        # Get current date for filenames
        current_date = datetime.now().strftime("%Y%m%d")
        project_slug = st.session_state.project_info['name'].lower().replace(" ", "_")
        
        with col1:
            st.download_button(
                label="Download Material Estimation (CSV)",
                data=materials_csv.getvalue(),
                file_name=f"{project_slug}_materials_{export_currency}_{export_units.lower().replace(' ', '_')}_{current_date}.csv",
                mime="text/csv"
            )
            
        with col2:
            st.download_button(
                label="Download Construction Schedule (CSV)",
                data=schedule_csv.getvalue(),
                file_name=f"{project_slug}_schedule_{current_date}.csv",
                mime="text/csv"
            )
            
        st.subheader("Project Summary Report")
        
        # Helper function to format dates for summary
        def format_date(date_obj):
            if hasattr(date_obj, 'date'):
                return date_obj.date().strftime("%Y-%m-%d")
            return date_obj.strftime("%Y-%m-%d")
        
        # Calculate start and end dates using the get_date helper for consistent date objects
        start_dates = [get_date(task['start_date']) for task in st.session_state.schedule]
        end_dates = [get_date(task['end_date']) for task in st.session_state.schedule]
        
        # Find earliest start and latest end
        earliest_start = min(start_dates)
        latest_end = max(end_dates)
        
        # Calculate duration
        project_duration = (latest_end - earliest_start).days
        
        # Calculate total cost in selected currency
        total_cost = sum(item.get('cost', 0) for item in export_materials)
        
        # Convert area to selected unit system if needed
        area_value = st.session_state.project_info['area_sqft']
        area_unit = "sq ft"
        
        if export_units == "Metric":
            area_value = area_value * 0.092903
            area_unit = "sq meters"
        elif export_units == "Imperial (UK)":
            area_unit = "sq feet"
            
        # Generate project summary with converted values
        summary = f"""
        # Project Summary Report
        
        ## Project Information
        - **Project Name:** {st.session_state.project_info['name']}
        - **Location:** {st.session_state.project_info['location']}
        - **Start Date:** {st.session_state.project_info['start_date']}
        - **Contractor:** {st.session_state.project_info['contractor']}
        - **Total Area:** {area_value:,.2f} {area_unit}
        
        ## Material Estimation Summary
        - **Total Material Cost:** {export_symbol}{total_cost:,.2f}
        - **Number of Material Types:** {len(st.session_state.materials)}
        - **Currency:** {export_currency}
        - **Unit System:** {export_units}
        
        ## Schedule Summary
        - **Project Start Date:** {format_date(earliest_start)}
        - **Project End Date:** {format_date(latest_end)}
        - **Project Duration:** {project_duration} days
        - **Number of Tasks:** {len(st.session_state.schedule)}
        
        ## Top 5 Most Expensive Materials
        """
        
        # Add top materials with converted values
        sorted_materials = sorted(export_materials, key=lambda x: x.get('cost', 0), reverse=True)[:5]
        for i, material in enumerate(sorted_materials, 1):
            cost = material.get('cost', 0)
            quantity = material.get('quantity', 0)
            unit = material.get('unit', '')
            summary += f"{i}. **{material['name']}**: {export_symbol}{cost:,.2f} ({quantity:,.2f} {unit})\n"
        
        st.markdown(summary)
        
        # Download summary report
        st.download_button(
            label="Download Project Summary Report (Markdown)",
            data=summary,
            file_name=f"{project_slug}_summary_{export_currency}_{current_date}.md",
            mime="text/markdown"
        )
        
        # Create Excel export with multiple sheets
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer) as writer:
            materials_df.to_excel(writer, sheet_name="Materials", index=False)
            schedule_df.to_excel(writer, sheet_name="Schedule", index=False)
            
            # Add project info as a separate sheet
            project_info_df = pd.DataFrame([{
                "Project Name": st.session_state.project_info['name'],
                "Location": st.session_state.project_info['location'],
                "Start Date": st.session_state.project_info['start_date'],
                "Contractor": st.session_state.project_info['contractor'],
                "Area": f"{area_value:,.2f} {area_unit}",
                "Total Cost": f"{export_symbol}{total_cost:,.2f}",
                "Currency": export_currency,
                "Units": export_units,
                "Project Duration": f"{project_duration} days",
                "Generated On": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            project_info_df.to_excel(writer, sheet_name="Project Info", index=False)
            
        # Offer Excel download
        st.download_button(
            label="Download Complete Project Report (Excel)",
            data=excel_buffer.getvalue(),
            file_name=f"{project_slug}_complete_report_{export_currency}_{export_units.lower().replace(' ', '_')}_{current_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
