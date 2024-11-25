import pandas

from .models import AutodeskConstructionCloudReport

ALLOWED_FIELDS = ['Last updated', 'Deliverable', 'Status', 'RIBA Stage', '% Complete']

def json_from_excel(file) -> str:
    df = pandas.read_excel(file, sheet_name='Files')[ALLOWED_FIELDS]

    df['Last updated'] = pandas.to_datetime(df['Last updated']).dt.date
    dates = pandas.DataFrame({'date': df['Last updated'], 'value': 1})
    dates = dates.groupby('date', as_index=False).sum()

    deliverables = df['Deliverable'].value_counts().rename_axis('deliverable').reset_index(name='value')

    statuses = df['Status'].value_counts().rename_axis('status').reset_index(name='value')

    df['RIBA Stage'] = pandas.to_numeric(df['RIBA Stage'], errors='coerce').astype('Int64')
    riba_stages = df['RIBA Stage'].value_counts().rename_axis('stage').reset_index(name='value')

    percents = df['% Complete'].value_counts().rename_axis('percent').reset_index(name='value')
    
    return {'last_updated': dates.to_json(orient='records'), 
            'deliverables': deliverables.to_json(orient='records'),
            'statuses': statuses.to_json(orient='records'),
            'riba_stages': riba_stages.to_json(orient='records'),
            'percents': percents.to_json(orient='records')}