import pandas

from .models import AutodeskConstructionCloudReport

def convert_to_bytes(size_str):
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
    ALLOWED_FIELDS = ['Last updated', 'File size', 'RIBA Stage', 'Version number', 'Status', 'Deliverable']
    df = pandas.read_excel(file, sheet_name='Files')[ALLOWED_FIELDS]

    df['Last updated'] = pandas.to_datetime(df['Last updated']).dt.date
    dates = pandas.DataFrame({'date': df['Last updated'], 'value': 1})
    dates = dates.groupby('date', as_index=False).sum()

    deliverables = df['Deliverable'].value_counts().rename_axis('deliverable').reset_index(name='value')

    statuses = df['Status'].value_counts().rename_axis('status').reset_index(name='value')

    df['RIBA Stage'] = pandas.to_numeric(df['RIBA Stage'], errors='coerce').astype('Int64')
    riba_stages = df['RIBA Stage'].value_counts().rename_axis('stage').reset_index(name='value')

    df['File size'] = df['File size'].apply(convert_to_bytes)
    file_sizes = df['File size']

    df['Version number'] = df['Version number'].apply(lambda val: val.replace('V', '')).astype(str)
    versions = df['Version number'].value_counts().rename_axis('version').reset_index(name='value')
    
    return {'last_updated': dates.to_json(orient='records'), 
            'file_sizes': file_sizes.to_json(orient='records'),
            'deliverables': deliverables.to_json(orient='records'),
            'statuses': statuses.to_json(orient='records'),
            'riba_stages': riba_stages.to_json(orient='records'),
            'versions': versions.to_json(orient='records')} 