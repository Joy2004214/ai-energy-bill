"""AI Energy Bill: local CSV analysis. Run: python -m streamlit run app.py"""
import math
from io import StringIO
import pandas as pd
import streamlit as st

REQUIRED = ['date', 'provider', 'model', 'input_tokens', 'output_tokens']
SAMPLE = '''date,provider,model,input_tokens,output_tokens,request_count,task_type,department
2026-10-01,OpenAI,demo-small,8000000,2000000,10000,customer_support,Support
2026-10-02,Anthropic,demo-large,4000000,1000000,1000,coding,Engineering
2026-10-03,Google,demo-small,0,0,0,document_analysis,Operations
'''
REGION_RECORDS = [{'region': 'Alabama', 'usd_per_kwh': 0.11900000000000001, 'kg_co2_per_kwh': 0.33883350039000004, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/alabama/'}, {'region': 'Alaska', 'usd_per_kwh': 0.2217, 'kg_co2_per_kwh': 0.5424964745199999, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/alaska/'}, {'region': 'Arizona', 'usd_per_kwh': 0.1274, 'kg_co2_per_kwh': 0.28757756258, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/arizona/'}, {'region': 'Arkansas', 'usd_per_kwh': 0.0959, 'kg_co2_per_kwh': 0.4354486752, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/arkansas/'}, {'region': 'California', 'usd_per_kwh': 0.2704, 'kg_co2_per_kwh': 0.18461209459, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/california/'}, {'region': 'Colorado', 'usd_per_kwh': 0.1207, 'kg_co2_per_kwh': 0.43454149046, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/colorado/'}, {'region': 'Connecticut', 'usd_per_kwh': 0.2437, 'kg_co2_per_kwh': 0.24539347217000002, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/connecticut/'}, {'region': 'Delaware', 'usd_per_kwh': 0.1356, 'kg_co2_per_kwh': 0.51074500862, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/delaware/'}, {'region': 'District of Columbia', 'usd_per_kwh': 0.16879999999999998, 'kg_co2_per_kwh': 0.42501605069000004, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/districtofcolumbia/'}, {'region': 'Florida', 'usd_per_kwh': 0.1253, 'kg_co2_per_kwh': 0.34699816305000003, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/florida/'}, {'region': 'Georgia', 'usd_per_kwh': 0.114, 'kg_co2_per_kwh': 0.30481407264, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/georgia/'}, {'region': 'Hawaii', 'usd_per_kwh': 0.38, 'kg_co2_per_kwh': 0.64682271962, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/hawaii/'}, {'region': 'Idaho', 'usd_per_kwh': 0.0951, 'kg_co2_per_kwh': 0.17327228534, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/idaho/'}, {'region': 'Illinois', 'usd_per_kwh': 0.12210000000000001, 'kg_co2_per_kwh': 0.2313321087, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/illinois/'}, {'region': 'Indiana', 'usd_per_kwh': 0.11380000000000001, 'kg_co2_per_kwh': 0.63185417141, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/indiana/'}, {'region': 'Iowa', 'usd_per_kwh': 0.0934, 'kg_co2_per_kwh': 0.31706106663000005, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/iowa/'}, {'region': 'Kansas', 'usd_per_kwh': 0.1121, 'kg_co2_per_kwh': 0.30844281160000003, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/kansas/'}, {'region': 'Kentucky', 'usd_per_kwh': 0.1007, 'kg_co2_per_kwh': 0.7910650932800001, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/kentucky/'}, {'region': 'Louisiana', 'usd_per_kwh': 0.08800000000000001, 'kg_co2_per_kwh': 0.42048012699000004, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/louisiana/'}, {'region': 'Maine', 'usd_per_kwh': 0.1966, 'kg_co2_per_kwh': 0.22089948419000002, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/maine/'}, {'region': 'Maryland', 'usd_per_kwh': 0.15039999999999998, 'kg_co2_per_kwh': 0.27396979148, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/maryland/'}, {'region': 'Massachusetts', 'usd_per_kwh': 0.2394, 'kg_co2_per_kwh': 0.42456245832, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/massachusetts/'}, {'region': 'Michigan', 'usd_per_kwh': 0.1416, 'kg_co2_per_kwh': 0.43408789809000004, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/michigan/'}, {'region': 'Minnesota', 'usd_per_kwh': 0.1235, 'kg_co2_per_kwh': 0.34745175542000006, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/minnesota/'}, {'region': 'Mississippi', 'usd_per_kwh': 0.1093, 'kg_co2_per_kwh': 0.36015234178000005, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/mississippi/'}, {'region': 'Missouri', 'usd_per_kwh': 0.1106, 'kg_co2_per_kwh': 0.66043049072, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/missouri/'}, {'region': 'Montana', 'usd_per_kwh': 0.10830000000000001, 'kg_co2_per_kwh': 0.43953100653, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/montana/'}, {'region': 'Nebraska', 'usd_per_kwh': 0.0907, 'kg_co2_per_kwh': 0.49078694434000003, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/nebraska/'}, {'region': 'Nevada', 'usd_per_kwh': 0.11470000000000001, 'kg_co2_per_kwh': 0.28621678547, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/nevada/'}, {'region': 'New Hampshire', 'usd_per_kwh': 0.2061, 'kg_co2_per_kwh': 0.12700586360000002, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/newhampshire/'}, {'region': 'New Jersey', 'usd_per_kwh': 0.1629, 'kg_co2_per_kwh': 0.22997133159, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/newjersey/'}, {'region': 'New Mexico', 'usd_per_kwh': 0.09179999999999999, 'kg_co2_per_kwh': 0.33701913091, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/newmexico/'}, {'region': 'New York', 'usd_per_kwh': 0.1966, 'kg_co2_per_kwh': 0.24357910269000002, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/newyork/'}, {'region': 'North Carolina', 'usd_per_kwh': 0.1165, 'kg_co2_per_kwh': 0.30390688790000003, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/northcarolina/'}, {'region': 'North Dakota', 'usd_per_kwh': 0.0793, 'kg_co2_per_kwh': 0.64591553488, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/northdakota/'}, {'region': 'Ohio', 'usd_per_kwh': 0.11289999999999999, 'kg_co2_per_kwh': 0.45586033185, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/ohio/'}, {'region': 'Oklahoma', 'usd_per_kwh': 0.0909, 'kg_co2_per_kwh': 0.30526766501, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/oklahoma/'}, {'region': 'Oregon', 'usd_per_kwh': 0.11109999999999999, 'kg_co2_per_kwh': 0.15966451424000003, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/oregon/'}, {'region': 'Pennsylvania', 'usd_per_kwh': 0.1251, 'kg_co2_per_kwh': 0.29891737183000006, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/pennsylvania/'}, {'region': 'Rhode Island', 'usd_per_kwh': 0.2415, 'kg_co2_per_kwh': 0.37557448236, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/rhodeisland/'}, {'region': 'South Carolina', 'usd_per_kwh': 0.109, 'kg_co2_per_kwh': 0.26716590593, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/southcarolina/'}, {'region': 'South Dakota', 'usd_per_kwh': 0.10869999999999999, 'kg_co2_per_kwh': 0.14424237366, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/southdakota/'}, {'region': 'Tennessee', 'usd_per_kwh': 0.109, 'kg_co2_per_kwh': 0.36468826548000005, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/tennessee/'}, {'region': 'Texas', 'usd_per_kwh': 0.09789999999999999, 'kg_co2_per_kwh': 0.37330652051, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/texas/'}, {'region': 'Utah', 'usd_per_kwh': 0.09970000000000001, 'kg_co2_per_kwh': 0.59964911314, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/utah/'}, {'region': 'Vermont', 'usd_per_kwh': 0.1841, 'kg_co2_per_kwh': 0.0036287389600000003, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/vermont/'}, {'region': 'Virginia', 'usd_per_kwh': 0.10619999999999999, 'kg_co2_per_kwh': 0.28621678547, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/virginia/'}, {'region': 'Washington', 'usd_per_kwh': 0.1013, 'kg_co2_per_kwh': 0.11294450013000001, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/washington/'}, {'region': 'West Virginia', 'usd_per_kwh': 0.1105, 'kg_co2_per_kwh': 0.8672686114400001, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/westvirginia/'}, {'region': 'Wisconsin', 'usd_per_kwh': 0.1272, 'kg_co2_per_kwh': 0.4944156833, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/wisconsin/'}, {'region': 'Wyoming', 'usd_per_kwh': 0.09140000000000001, 'kg_co2_per_kwh': 0.78199324588, 'data_year': 2024, 'price_sector': 'all sectors', 'emissions_basis': 'in-state generation, direct CO2; excludes imports and lifecycle', 'source_url': 'https://www.eia.gov/electricity/state/wyoming/'}]
REGIONS = {r['region']: (r['usd_per_kwh'], r['kg_co2_per_kwh']) for r in REGION_RECORDS}
PROXIES = {'small': (0.1, 0.2, 0.4), 'large': (0.5, 1.0, 2.0)}


def numbers(series, label, integer=False, optional=False):
    blank = series.isna() | series.astype(str).str.strip().eq('')
    result = pd.to_numeric(series, errors='coerce')
    valid = result.map(lambda x: pd.notna(x) and math.isfinite(x) and x >= 0 and (not integer or float(x).is_integer()))
    if optional:
        valid = valid | blank
    if not valid.all():
        raise ValueError(f'{label}: use finite nonnegative ' + ('whole numbers.' if integer else 'numbers.'))
    return result


def validate_usage(raw):
    df = raw.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
    if df.columns.duplicated().any():
        raise ValueError('Duplicate column names after normalization.')
    missing = set(REQUIRED) - set(df.columns)
    if missing:
        raise ValueError('Missing columns: ' + ', '.join(sorted(missing)))
    if df.empty:
        raise ValueError('The CSV has no usage rows.')
    for col in ['provider', 'model']:
        if df[col].isna().any() or df[col].astype(str).str.strip().eq('').any():
            raise ValueError(f'{col} is required in every row.')
        df[col] = df[col].astype(str).str.strip()
    # Canonical input requires calendar dates; relative BurstGPT seconds need explicit conversion.
    date_text = df.date.astype(str).str.strip()
    if not date_text.str.fullmatch(r'\d{4}-\d{2}-\d{2}').all():
        raise ValueError('date must be YYYY-MM-DD. Convert relative timestamps before upload.')
    df['date'] = pd.to_datetime(date_text, format='%Y-%m-%d', errors='coerce')
    if df.date.isna().any():
        raise ValueError('Some calendar dates are invalid.')
    for col in ['input_tokens', 'output_tokens']:
        df[col] = numbers(df[col], col, integer=True)
    df['total_tokens'] = df.input_tokens + df.output_tokens
    if 'request_count' in df:
        df['request_count'] = numbers(df.request_count, 'request_count', integer=True, optional=True)
        if ((df.request_count == 0) & (df.total_tokens > 0)).any():
            raise ValueError('Positive tokens cannot have request_count=0. Leave unknown counts blank.')
    if 'actual_cost_usd' in df:
        df['actual_cost_usd'] = numbers(df.actual_cost_usd, 'actual_cost_usd', optional=True)
    for col in ['task_type', 'department']:
        if col not in df:
            df[col] = 'Unspecified'
        df[col] = df[col].fillna('Unspecified').astype(str).str.strip().replace('', 'Unspecified')
    if 'request_id' in df and df.request_id.notna().any():
        known = df.dropna(subset=['request_id'])
        if known.duplicated(['provider', 'request_id']).any():
            raise ValueError('Duplicate request IDs within a provider. Check for repeated exports.')
    return df


def parameter_template(df, demo=False):
    rows = []
    for provider, model in df[['provider', 'model']].drop_duplicates().itertuples(index=False, name=None):
        category = 'small' if model == 'demo-small' else 'large'
        factors = PROXIES[category] if demo else (None, None, None)
        rows.append(dict(provider=provider, model=model,
            input_usd_per_million=(1.0 if category == 'small' else 5.0) if demo else None,
            output_usd_per_million=(5.0 if category == 'small' else 15.0) if demo else None,
            wh_low=factors[0], wh_typical=factors[1], wh_high=factors[2],
            **{f'{phase}_wh_{level}': None for phase in ['input','output'] for level in ['low','typical','high']},
            includes_pue=False, energy_basis='illustrative category proxy' if demo else 'not supplied',
            price_source='DEMO fixture' if demo else '', energy_source='DEMO fixture' if demo else ''))
    return pd.DataFrame(rows)


def validate_parameters(params):
    p = params.copy()
    split_cols = [f'{phase}_wh_{level}' for phase in ['input','output'] for level in ['low','typical','high']]
    for col in split_cols:
        if col not in p: p[col] = float('nan')
    for col in ['input_usd_per_million', 'output_usd_per_million', 'wh_low', 'wh_typical', 'wh_high'] + split_cols:
        p[col] = numbers(p[col], col, optional=True)
    for row in p.itertuples():
        split = [getattr(row, c) for c in split_cols]
        if any(pd.notna(x) for x in split):
            if not all(pd.notna(x) for x in split):
                raise ValueError(f'{row.model}: supply all six input/output energy factors.')
            for phase in ['input','output']:
                a,b,c = [getattr(row, f'{phase}_wh_{level}') for level in ['low','typical','high']]
                if not a <= b <= c: raise ValueError(f'{row.model}: split factors must be ordered low ≤ typical ≤ high.')
        fs = [row.wh_low, row.wh_typical, row.wh_high]
        supplied = [pd.notna(x) for x in fs]
        if any(supplied) and not all(supplied):
            raise ValueError(f'{row.model}: supply all three energy factors or leave all blank.')
        if all(supplied) and not (fs[0] <= fs[1] <= fs[2]):
            raise ValueError(f'{row.model}: energy factors must satisfy low ≤ typical ≤ high.')
    return p


def calculate(df, params, pue):
    out = df.merge(params, on=['provider', 'model'], how='left', validate='many_to_one')
    out['api_usd'] = (out.input_tokens * out.input_usd_per_million + out.output_tokens * out.output_usd_per_million) / 1e6
    overhead = out.includes_pue.fillna(False).map(lambda x: 1.0 if x else pue)
    for level in ['low', 'typical', 'high']:
        legacy = out.total_tokens * out['wh_' + level] / 1e6
        split = (out.input_tokens * out['input_wh_' + level] + out.output_tokens * out['output_wh_' + level]) / 1e6
        out['kwh_' + level] = split.where(split.notna(), legacy) * overhead
    out['energy_method_used'] = out.input_wh_typical.notna().map({True: 'separate input/output factors', False: 'combined-token proxy'})
    return out


def complete_total(df, col):
    # Never report a partial sum as a company-wide total.
    relevant = df.total_tokens > 0
    if df.loc[relevant, col].isna().any():
        return None
    return float(df[col].sum())


def fmt(value, unit='', money=False):
    return 'Needs data' if value is None else (f'${value:,.2f}' if money else f'{value:,.2f}{unit}')



def convert_burstgpt(raw, origin):
    """Preserve original model labels; origin is an explicit display anchor, not a discovered date."""
    d = raw.copy()
    d.columns = d.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
    required = {'timestamp','model','request_tokens','response_tokens','log_type'}
    if not required.issubset(d): raise ValueError('Not a recognized BurstGPT schema.')
    seconds = numbers(d.timestamp, 'Timestamp')
    inp = numbers(d.request_tokens, 'Request tokens', integer=True)
    out = numbers(d.response_tokens, 'Response tokens', integer=True)
    if 'total_tokens' in d and not numbers(d.total_tokens, 'Total tokens', integer=True).eq(inp+out).all():
        raise ValueError('BurstGPT Total tokens does not equal request + response tokens.')
    stamp = pd.Timestamp(origin) + pd.to_timedelta(seconds, unit='s')
    converted = pd.DataFrame(dict(date=stamp.dt.strftime('%Y-%m-%d'), provider='Azure OpenAI',
        model=d.model, input_tokens=inp, output_tokens=out, request_count=1,
        usage_channel=d.log_type, relative_day=(seconds//86400+1).astype(int)))
    # Channel is not a task type. Zero-response rows are retained, not interpreted as quality failures.
    return validate_usage(converted)


def workload_evidence(df):
    """Daily paired differences; never test estimated energy against its own coefficients."""
    daily = df.groupby('date')[['input_tokens','output_tokens']].sum()
    daily['output_minus_input'] = daily.output_tokens-daily.input_tokens
    report = {'rows':len(df), 'observed_days':len(daily),
        'input_tokens':int(df.input_tokens.sum()), 'output_tokens':int(df.output_tokens.sum()),
        'hypothesis':'H0: mean daily output tokens minus input tokens = 0; two-sided',
        'status':'Insufficient: need at least 7 observed days and nonzero daily variation.'}
    if len(daily)>=7 and daily.output_minus_input.std()>0:
        try:
            from scipy.stats import ttest_1samp, t
            delta=daily.output_minus_input
            test=ttest_1samp(delta, 0)
            margin=t.ppf(.975,len(delta)-1)*delta.sem()
            report.update(status='Exploratory; assumes independent days. Serial dependence may invalidate p-values.',
                mean_daily_difference=float(delta.mean()), ci95_low=float(delta.mean()-margin),
                ci95_high=float(delta.mean()+margin), p_value=float(test.pvalue),
                n_days=len(delta), test='one-sample t-test of paired daily differences')
        except ImportError:
            report['status']='Install scipy to enable the exploratory test.'
    return daily, report


def evidence_panel(scoped):
    st.subheader('Workload evidence and hypothesis')
    st.caption('Observed usage only. This does not test energy consumption, task quality or a causal model effect.')
    daily, report = workload_evidence(scoped)
    total = scoped.total_tokens.sum()
    st.metric('Output share of observed tokens', f'{scoped.output_tokens.sum()/total:.1%}' if total else 'N/A')
    st.line_chart(daily[['input_tokens','output_tokens']])
    st.write(report)
    st.caption('Observed days are not automatically independent. Missing days are not treated as zero. The test is exploratory and can reflect task mix, channels or changing traffic. Pre-specify a hypothesis and use a longer representative trace for confirmation. A nonsignificant result does not establish equality.')
    st.download_button('Download workload evidence', pd.DataFrame([report]).to_csv(index=False), 'workload_evidence.csv', 'text/csv')




def ui_icon(name):
    paths = {
        'upload': '<path d="M12 16V3m-5 5 5-5 5 5M4 16v5h16v-5"/>',
        'chart': '<path d="M4 3v17h17M8 15v-4m5 4V7m5 8v-6"/>',
        'spark': '<path d="m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5Z"/>',
        'cost': '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M16 10h5v4h-5zM7 9h4"/>',
        'energy': '<path d="m13 2-9 12h7l-1 8 10-12h-7Z"/>',
        'bill': '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2ZM9 8h6m-6 4h6"/>',
        'leaf': '<path d="M20 4C8 2 2 9 6 16s16 2 14-12ZM5 21 16 10"/>'}
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths[name]+'</svg>'


def apply_design():
    st.markdown("""<style>
    :root {color-scheme:light;}
    .stApp {background:#F4F7FB;color:#172C46;}
    [data-testid="stHeader"] {background:transparent;}
    .block-container {padding-top:2rem;padding-bottom:2rem;max-width:1400px;}
    [data-testid="stSidebar"] {background:#FFFFFF;border-right:1px solid #DFE7EF;}
    [data-testid="stSidebar"] .block-container {padding-top:1.5rem;}
    h1,h2,h3 {color:#172C46;letter-spacing:-.035em;}
    h2 {font-size:1.5rem!important;} h3 {font-size:1.15rem!important;}
    p, label {color:#334C65;}
    .hero {background:linear-gradient(115deg,#132C46 0%,#174859 70%,#127A78 100%);padding:32px 36px;border-radius:22px;margin-bottom:22px;}
    .hero-mark {float:right;width:78px;height:78px;background:#FFFFFF15;padding:16px;border-radius:20px;color:#8CEBD6;}
    .hero-mark svg {width:100%;height:100%;}
    .step {display:flex;align-items:center;gap:14px;}
    .step-icon {width:44px;height:44px;flex-shrink:0;color:#098B80;}
    .step-icon svg {width:44px;height:44px;}
    .metric-icon {width:52px;height:52px;background:#E1F6F0;border-radius:14px;color:#087F78;padding:11px;margin:12px 0 8px;}
    .metric-icon svg {width:30px;height:30px;}
    .hero .eyebrow {color:#89E2D2;font-size:12px;letter-spacing:.16em;font-weight:700;}
    .hero h1 {color:white!important;font-size:38px!important;margin:8px 0;line-height:1.2;}
    .hero p {color:#D5E8F1;margin:0;max-width:650px;font-size:16px;}
    .brand {font-size:20px;font-weight:750;letter-spacing:-.6px;color:#172C46;margin-bottom:6px;}
    .brand span {color:#087F78;}
    .steps {display:flex;gap:12px;margin:0 0 24px;flex-wrap:wrap;}
    .step {background:white;border:1px solid #DCE5EF;border-radius:12px;padding:12px 18px;flex:1;min-width:160px;color:#405B73;font-size:14px;}
    .step b {display:inline-block;color:#087F78;margin-right:10px;}
    [data-testid="stMetric"] {background:white;border:1px solid #E0E7EF;border-radius:16px;padding:20px;box-shadow:0 4px 14px #18334D05;min-height:124px;}
    [data-testid="stMetricValue"] {font-size:32px;color:#172C46;font-weight:700;letter-spacing:-1px;}
    [data-testid="stMetricLabel"] p {font-size:13px;color:#5B7085;}
    [data-testid="stExpander"] {background:#FFFFFF;border:1px solid #DFE7EF;border-radius:12px;}
    .stButton>button, .stDownloadButton>button {border-radius:10px;border-color:#D5E1EA;color:#174859;background:white;}
    .stButton>button:hover,.stDownloadButton>button:hover {border-color:#0E9288;color:#087F78;background:#ECFAF6;}
    [data-baseweb="tab-list"] {gap:8px;padding:8px 0;}
    [data-baseweb="tab"] {border-radius:10px;padding:12px 20px;background:#EAF0F6;color:#405B73;}
    [aria-selected="true"][role="tab"] {background:#DDF5EE;color:#087F78;font-weight:700;}
    [data-testid="stAlert"] {border-radius:12px;}
    [data-testid="stFileUploader"] {border-radius:14px;}
    @media(max-width:760px){.hero{padding:24px}.hero h1{font-size:29px!important}.block-container{padding-top:1rem}[data-testid="stMetricValue"]{font-size:26px}}
    </style>""", unsafe_allow_html=True)


def main():
    st.set_page_config(page_title='AI Energy Bill', page_icon='⚡', layout='wide', initial_sidebar_state='expanded')
    apply_design()
    st.markdown('<div class="hero"><div class="hero-mark">'+ui_icon('energy')+'</div><div class="eyebrow">AI ENERGY BILL · US EDITION</div><h1>Your AI. A clearer picture.</h1><p>Costs, energy & smarter choices.</p></div>', unsafe_allow_html=True)
    steps = [('upload','Upload CSV'), ('chart','View impact'), ('spark','Explore savings')]
    st.markdown('<div class="steps">'+''.join('<div class="step"><span class="step-icon">'+ui_icon(icon)+'</span><span>'+label+'</span></div>' for icon,label in steps)+'</div>', unsafe_allow_html=True)
    with st.sidebar:
        st.markdown('<div class="brand">⚡ AI Energy <span>Bill</span></div>', unsafe_allow_html=True)
        st.caption('Costs. Energy. Clarity.')
        st.divider()
        st.subheader('1 · Add your usage')
        mode = st.radio('Usage source', ['Sample data', 'Upload CSV', 'Enter manually'])
        st.caption('Try Sample data first.')
    template = pd.read_csv(StringIO(SAMPLE))
    st.sidebar.download_button('Download CSV template', SAMPLE, 'usage_template.csv', 'text/csv')
    with st.sidebar.expander('What should my CSV include?'):
        st.write('Required: date, provider, model, input_tokens, output_tokens. Optional: request_count, task_type, department, actual_cost_usd, inference_region.')
        st.write('Use one row per day × provider × exact model × task/department, or nonoverlapping request records. Never combine aggregates with their underlying logs. Duplicate-looking rows are flagged, not silently deleted.')
        st.write('Use total-period token counts. Do not upload prompts, customer names, API keys or confidential text. Use anonymized task labels. Existing small/large-only CSVs must be converted to this schema.')
        st.write('BurstGPT: Request tokens → input_tokens; Response tokens → output_tokens. Timestamp is relative seconds, so explicitly establish a date origin before conversion. Retain hosting platform and original model identifiers; do not infer a current model version.')
    demo = mode == 'Sample data'
    if demo:
        raw = template
        st.info('Demo · Illustrative model assumptions · EIA 2024 regional data')
    elif mode == 'Enter manually':
        raw = st.data_editor(template.iloc[:0], num_rows='dynamic', key='manual')
    else:
        file = st.sidebar.file_uploader('Choose your usage CSV', type='csv', help='Upload a UTF-8 CSV. Your file is processed by this app without external AI calls.')
        if file is None:
            st.info('← Add your usage CSV in the sidebar, or choose Sample data to take a look around.'); return
        try:
            raw = pd.read_csv(file)
        except Exception:
            st.error('Cannot read this CSV. Use a UTF-8 comma-separated file.'); return
    try:
        if {'Timestamp','Request tokens','Response tokens'}.issubset(raw.columns):
            st.info('BurstGPT detected. Original model labels and zero-response records are preserved. Dates below use your chosen display anchor.')
            origin = st.date_input('Day 1 display anchor (not a verified dataset start date)', value=pd.Timestamp('2000-01-01').date())
            usage = convert_burstgpt(raw, origin)
            channels = st.multiselect('BurstGPT usage channels', sorted(usage.usage_channel.unique()), default=sorted(usage.usage_channel.unique()))
            usage = usage[usage.usage_channel.isin(channels)]
            if usage.empty: st.info('Select at least one channel.'); return
            st.download_button('Download converted trace', usage.to_csv(index=False), 'converted_usage.csv', 'text/csv')
        else:
            usage = validate_usage(raw)
    except ValueError as error:
        st.error(str(error)); return
    if usage.duplicated(REQUIRED + ['task_type', 'department']).any():
        st.warning('Some rows have identical dates, models, tokens and task labels. Check for duplicate exports; no rows were removed.')
    st.sidebar.success(f'Ready · {len(usage):,} rows across {len(usage[["provider", "model"]].drop_duplicates())} provider/model pairs.')
    with st.expander('Preview validated usage'):
        st.dataframe(usage, hide_index=True)

    with st.sidebar:
        st.subheader('2 · Choose your scope')
        d1, d2 = st.columns(2)
        start = d1.date_input('Start date', usage.date.min().date(), key='filter_start')
        end = d2.date_input('End date', usage.date.max().date(), key='filter_end')
        if start > end:
            st.error('End date must not be before start date.'); return
        scoped = usage[(usage.date >= pd.Timestamp(start)) & (usage.date <= pd.Timestamp(end))].copy()
        tasks = st.multiselect('Task types (empty means all)', sorted(usage.task_type.unique()))
        if tasks:
            scoped = scoped[scoped.task_type.isin(tasks)].copy()
        if scoped.empty:
            st.info('No usage in this scope.'); return
        st.caption('Results cover the selected dates.')

    with st.expander('Model assumptions · prices & energy factors', expanded=False):
        st.write('Each provider/model pair has its own rates. Blank means unknown; zero means genuinely zero.')
        st.caption('Prices: USD per million tokens. Energy: Wh per 1,000 tokens. Supply all six input_wh/output_wh factors to use separate phases; otherwise the combined wh factors are an explicitly labeled fallback. Model names alone never imply an energy factor.')
        cfg = parameter_template(usage, demo)
        params = st.data_editor(cfg, hide_index=True, disabled=['provider', 'model'], key='params_demo' if demo else 'params_' + str(hash(usage[['provider','model']].to_csv(index=False))), column_config={
            'includes_pue': st.column_config.CheckboxColumn('Energy includes PUE?'),
            **{c: st.column_config.NumberColumn(c, min_value=0.0) for c in ['input_usd_per_million','output_usd_per_million','wh_low','wh_typical','wh_high'] + [f'{phase}_wh_{level}' for phase in ['input','output'] for level in ['low','typical','high']]}})
        st.caption('Enter source URLs or assumption notes. Record applicable price tier/date in price_source and energy method/date in energy_source. A source note does not automatically validate a number.')
        pue = st.number_input('PUE for factors that exclude facility overhead', min_value=1.0, max_value=3.0, value=1.2, step=0.1)
        try:
            params = validate_parameters(params)
            result = calculate(scoped, params, pue)
        except (ValueError, TypeError) as error:
            st.error(str(error)); return
        st.download_button('Download model assumptions', params.to_csv(index=False), 'model_assumptions.csv', 'text/csv')
    unknown_price = result.loc[(result.total_tokens > 0) & result.api_usd.isna(), ['provider','model']].drop_duplicates()
    unknown_energy = result.loc[(result.total_tokens > 0) & result.kwh_typical.isna(), ['provider','model']].drop_duplicates()
    if len(unknown_price):
        st.warning('Next step: open Model assumptions and add prices for ' + ', '.join(unknown_price.model))
    if len(unknown_energy):
        st.warning('Next step: open Model assumptions and add energy factors for ' + ', '.join(unknown_energy.model))

    st.subheader('Your AI impact at a glance')
    st.write(f'{start} – {end} · {result.total_tokens.sum():,.0f} tokens')
    region_name = st.sidebar.selectbox('Assumed inference region', ['Unknown'] + list(REGIONS))
    st.sidebar.caption('Choose a scenario region. Unsure? Keep Unknown.')
    with st.expander('Regional sources · EIA 2024'):
        region_df = pd.DataFrame(REGION_RECORDS)
        regions = st.data_editor(region_df, hide_index=True, disabled=list(region_df.columns), key='regions_2024')
        st.caption('51 jurisdictions · EIA 2024 state profiles · annual all-sector retail prices; these are not industrial tariffs or negotiated data-center contracts. CO₂ factors describe in-state generation, not electricity consumption adjusted for imports. This is a screening proxy, not a Scope 2 inventory.')
        st.download_button('Download all US regional data with sources', region_df.to_csv(index=False), 'us_regions_2024.csv', 'text/csv')
        region_note = st.text_input('Regional source / year / sector / emissions basis', 'EIA State Electricity Profiles 2024; all-sector retail prices; in-state generation direct CO2; retrieved 2026-11-06')
    try:
        for col in ['usd_per_kwh','kg_co2_per_kwh']:
            regions[col] = numbers(regions[col], col)
    except ValueError as error:
        st.error(str(error)); return
    region_map = regions.set_index('region')
    api = complete_total(result, 'api_usd')
    energy = {level: complete_total(result, 'kwh_' + level) for level in ['low','typical','high']}
    known_region = region_name != 'Unknown'
    price = float(region_map.loc[region_name, 'usd_per_kwh']) if known_region else None
    carbon = float(region_map.loc[region_name, 'kg_co2_per_kwh']) if known_region else None
    cols = st.columns(4)
    for col, icon in zip(cols, ['cost','energy','bill','leaf']):
        col.markdown('<div class="metric-icon">'+ui_icon(icon)+'</div>', unsafe_allow_html=True)
    cols[0].metric('Estimated standard API charges', fmt(api, money=True))
    cols[1].metric('Estimated electricity', fmt(energy['typical'], ' kWh'))
    cols[2].metric('Embedded electricity cost', fmt(energy['typical'] * price if known_region and energy['typical'] is not None else None, money=True))
    cols[3].metric('Estimated CO₂', fmt(energy['typical'] * carbon if known_region and energy['typical'] is not None else None, ' kg'))
    if energy['low'] is not None:
        st.caption(f'Energy low–high: {energy["low"]:.2f}–{energy["high"]:.2f} kWh. Scenario bounds, not confidence intervals.')
    st.caption('Estimates, not measured electricity. Electricity cost is not an extra API charge.')
    overview_tab, budget_tab, region_tab = st.tabs(['Usage overview', 'Optimize your budget', 'Compare US regions'])
    with overview_tab:
        if 'actual_cost_usd' in result:
            if result.actual_cost_usd.notna().all():
                actual = float(result.actual_cost_usd.sum())
                st.metric('Uploaded actual charges (same rows)', fmt(actual, money=True))
                if api is not None:
                    st.caption(f'Standard-rate estimate minus actual: ${api - actual:,.2f}; not necessarily an error or savings.')
            else:
                st.info('Actual charges are incomplete; no company-wide actual total is displayed.')
        if 'request_count' in result and result.request_count.notna().all() and result.request_count.sum() > 0:
            requests = result.request_count.sum()
            st.write(f'{requests:,.0f} requests · {result.total_tokens.sum()/requests:,.0f} tokens/request')
            if api is not None:
                st.write(f'Estimated API cost per 1,000 requests: ${api/requests*1000:.2f}')
        st.dataframe(result.groupby(['provider','model','task_type'], dropna=False).agg(input_tokens=('input_tokens','sum'), output_tokens=('output_tokens','sum'), rows=('date','size')).reset_index(), hide_index=True)
        st.subheader('Usage over time')
        st.bar_chart(result.groupby('date')[['input_tokens','output_tokens']].sum(), color=['#4263EB','#11A693'])

        with st.expander('Advanced · workload evidence and hypothesis'):
            evidence_panel(scoped)

    with budget_tab:
        st.subheader('Plan your next move')
        budget = st.number_input('API budget for this same selected period (USD)', min_value=0.0, value=100.0)
        growth = st.slider('Expected proportional workload growth (%)', 0, 200, 0, 5)
        multiplier = 1 + growth / 100
        if api is not None:
            projected = api * multiplier
            st.metric('Projected API charges with growth', fmt(projected, money=True))
            st.metric('Budget headroom', fmt(budget - projected, money=True))
            if projected > budget:
                st.warning(f'Requires at least {(1-budget/projected)*100:.1f}% lower average spend per task, assuming unchanged task mix and proportional usage.')
            choices = params[['provider','model']].apply(lambda r: r.provider + ' / ' + r.model, axis=1).tolist()
            src_label = st.selectbox('Current model to partially replace', choices)
            src = params.iloc[choices.index(src_label)]
            dst_label = st.selectbox('Candidate model (from parameter table)', choices)
            dst = params.iloc[choices.index(dst_label)]
            st.caption('Add a candidate-only row in the usage file with zero tokens to make another model available, then fill its parameters. No energy is inferred from price.')
            shift = st.slider('Selected model tokens shifted (%)', 0, 100, 0, 10) / 100
            if src_label != dst_label:
                scenario_usage = scoped.copy()
                mask = (scoped.provider == src.provider) & (scoped.model == src.model)
                moved = scoped.loc[mask].copy()
                for col in ['input_tokens','output_tokens']:
                    moved[col] *= shift
                    scenario_usage.loc[mask, col] *= 1-shift
                moved['provider'], moved['model'] = dst.provider, dst.model
                scenario_usage = pd.concat([scenario_usage, moved], ignore_index=True)
                scenario_usage['total_tokens'] = scenario_usage.input_tokens + scenario_usage.output_tokens
                scenario = calculate(scenario_usage, params, pue)
                new_api = complete_total(scenario, 'api_usd')
                new_energy = complete_total(scenario, 'kwh_typical')
                if new_api is not None:
                    new_cost = new_api * multiplier
                    savings = projected - new_cost
                    st.metric('Scenario API charges with growth', fmt(new_cost, money=True))
                    st.metric('Savings versus growth baseline', fmt(savings, money=True))
                    if shift > 0:
                        st.info(f'Rule-based: pilot {dst_label} on suitable tasks covering {shift*100:.0f}% of {src_label} token volume. Estimated API change: ${-savings:+.2f} for the selected period with growth. Validate success rate, latency, retries and human rework before expanding.')
                        if new_cost > budget:
                            st.warning(f'This scenario is still ${new_cost-budget:.2f} above budget.')
                else:
                    st.info('Candidate API prices are missing; scenario charges unavailable.')
                if new_energy is not None:
                    st.write(f'Scenario energy with growth: {new_energy*multiplier:.2f} kWh.')
                st.caption('Assumes unchanged token counts across models, output lengths, task mix and no additional retries. This is not evidence of equal quality. Scenario values are fractional expected volumes, not actual logged counts.')
            else:
                st.info('Select a different candidate to explore a pilot. Choose task-specific candidates; token logs alone do not establish task quality.')
        else:
            st.info('Complete baseline API rates to enable budget comparisons.')

    with region_tab:
        st.subheader('One workload. 51 regional scenarios.')
        st.caption('Compare the same workload. Regional screening, not a siting recommendation.')
        if energy['typical'] is not None:
            comparison = regions.copy()
            comparison['electricity_usd'] = comparison.usd_per_kwh * energy['typical']
            comparison['co2_kg'] = comparison.kg_co2_per_kwh * energy['typical']
            comparison['electricity_rank'] = comparison.electricity_usd.rank(method='min').astype(int)
            comparison['co2_rank'] = comparison.co2_kg.rank(method='min').astype(int)
            order = st.selectbox('Rank all jurisdictions by', ['Electricity cost', 'Generation-based CO₂'])
            comparison = comparison.sort_values('electricity_usd' if order == 'Electricity cost' else 'co2_kg')
            with st.expander('View all 51 regional rankings'):
                st.dataframe(comparison[['region','electricity_rank','co2_rank','electricity_usd','co2_kg','data_year']], hide_index=True)
            st.caption('Ties share a rank. CO₂ rankings reflect rounded in-state generation factors; imports and actual electricity contracts can change the comparison. A zero factor is not proof of zero lifecycle emissions.')
            candidates = st.multiselect('Compare candidate states (up to 8)', sorted(regions.region), default=['California','Texas','Virginia'], max_selections=8)
            subset = comparison[comparison.region.isin(candidates)].set_index('region')
            if len(subset):
                a,b = st.columns(2)
                a.bar_chart(subset[['electricity_usd']])
                b.bar_chart(subset[['co2_kg']])
            st.download_button('Download US scenario comparison', comparison.to_csv(index=False), 'us_region_comparison.csv', 'text/csv')
        else:
            st.info('Complete energy factors to compare the same workload across all US regions. Regional source data are available above.')
    st.divider()
    st.subheader('Take your results with you')
    st.caption('Download results and keep your assumptions alongside them.')
    result['assumed_region'] = region_name
    result['regional_source_note'] = region_note
    result['regional_data_year'] = 2024
    result['regional_source_url'] = region_map.loc[region_name,'source_url'] if known_region else ''
    result['pue_used_if_excluded'] = pue
    result['electricity_usd'] = result.kwh_typical * price if known_region else float('nan')
    result['co2_kg'] = result.kwh_typical * carbon if known_region else float('nan')
    st.download_button('Download analyzed rows', result.to_csv(index=False), 'ai_energy_analysis.csv', 'text/csv')
    with st.expander('Methodology & estimate limitations'):
        st.write('API charges exclude caching, tools, batch discounts, context tiers, subscriptions, taxes and negotiated terms. Region is a workload-wide assumption, not company address; uploaded per-row regions are preserved but not automatically mapped. No monthly extrapolation is applied.')
        st.write('API USD = input tokens × input USD/1M ÷ 1M + output tokens × output USD/1M ÷ 1M.')
        st.write('When available: kWh = (input tokens × input Wh/1k + output tokens × output Wh/1k) / 1,000,000 × applicable PUE. Six split factors override combined factors. Otherwise kWh = total tokens × Wh/1,000 tokens ÷ 1,000,000 × PUE; multiply by 1 instead if factors include PUE. Low/typical/high are assumptions, not statistical intervals.')
        st.write('Missing factors disable whole-scope totals rather than showing misleading partial sums. Zero-token candidate rows do not block totals. Actual charges are not inferred from token counts.')
        st.write('Siting feasibility still requires supply capacity, connection time, contracts, cooling/water, land, network and permits. Uploaded region labels are not automatically resolved. All comparisons use your chosen workload-wide scenario. No claims about peak power, measured efficiency or carbon neutrality are made.')


if __name__ == '__main__':
    main()
