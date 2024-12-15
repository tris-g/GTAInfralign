import pandas, json

from .models import AutodeskConstructionCloudReport

ALLOWED_FIELDS = ['Last updated', 'File size', 'RIBA Stage', 'Version number', 'Status', 'Deliverable']
STATUS_ORDER = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'S0', 'S1', 'S2', 'S3', 'S4', 'S5']

def verbose_user(request) -> str:
    """Returns a unique string representing the user within the request. Meant for logging purposes."""
    return f"{request.user.pk}:{request.user.username}"

def convert_to_bytes(size_str: str):
    """Convert a file size string like '1.3 MB' or '567 KB' to bytes."""
    size_units = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
    
    # Split the string into the numeric part and the unit
    size_str = size_str.strip()
    try:
        number, unit = size_str.split()
        number = float(number)
        unit = unit.upper()
    except ValueError:
        raise ValueError(f"Invalid size format: '{size_str}'")
    
    if unit not in size_units:
        raise ValueError(f"Unknown unit: '{unit}'")
    
    return int(number * size_units[unit])

def json_from_excel(file) -> str:
    # Read only the expected fields
    df = pandas.read_excel(file, sheet_name='Files')[ALLOWED_FIELDS]
    # Convert 'Last updated' to datetime.date
    df['Last updated'] = pandas.to_datetime(df['Last updated']).dt.date
    # Create a DataFrame with 'date' and 'value'
    dates = pandas.DataFrame({'date': df['Last updated'], 'value': 1})
    # Group by 'date' to get the sum of values (if there are duplicates)
    dates = dates.groupby('date', as_index=False).sum()
    # Ensure 'value' is an integer
    dates['value'] = dates['value'].astype(int)
    # Convert 'date' to epoch timestamps in milliseconds and as strings
    dates['date'] = (pandas.to_datetime(dates['date']).astype('int64') // 10**6)
    # Count the deliverables and format the frame
    deliverables = df['Deliverable'].value_counts().rename_axis('deliverable').reset_index(name='value')
    # Count the statuses and format the frame
    statuses = df['Status'].value_counts().rename_axis('status').reset_index(name='value')
    # Convert the 'status' column to a categorical type with the custom order
    statuses['status'] = pandas.Categorical(statuses['status'], categories=STATUS_ORDER, ordered=True)
    # Sort by the custom order
    statuses = statuses.sort_values('status').reset_index(drop=True)
    # Ensure each 'stage' is an integer, count the stages and format the frame
    df['RIBA Stage'] = pandas.to_numeric(df['RIBA Stage'], errors='coerce').astype('Int64')
    riba_stages = df['RIBA Stage'].value_counts().rename_axis('stage').reset_index(name='value')
    # Convert the storage string representations into byte integers
    df['File size'] = df['File size'].apply(convert_to_bytes)
    file_sizes = df['File size']
    # Count the versions and format the frame
    df['Version number'] = df['Version number'].apply(lambda val: val.replace('V', '')).astype(str)
    versions = df['Version number'].value_counts().rename_axis('version').reset_index(name='value')
    
    return {'last_updated': dates.to_dict(orient='records'),
            'file_sizes': file_sizes.to_dict(),
            'deliverables': deliverables.to_dict(orient='records'),
            'statuses': statuses.to_dict(orient='records'),
            'riba_stages': riba_stages.to_dict(orient='records'),
            'versions': versions.to_dict(orient='records')}