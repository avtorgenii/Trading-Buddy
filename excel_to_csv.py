import pandas as pd
from datetime import datetime, time

def excel_to_csv(excel):
    # Load the Excel file
    file_path = 'Journal.xlsx'
    df = pd.read_excel(file_path, nrows=146)

    # Convert the DataFrame to a list of dictionaries

    df = df.rename(columns={
        'Дата': 'date',
        '№ сделки': 'trade_id',
        'Инструмент': 'tool',
        'Тип сделки': 'side',
        'Tags': 'tags',
        'Время входа': 'time',
        'Причина входа': 'reason_of_entry',
        'Цена входа': 'price_of_entry',
        'Лотов/ контрактов': 'volume',
        'Цена выхода': 'price_of_exit',
        'Причина выхода': 'reason_of_exit',
        'Прибыль/ убыток в usdt.': 'pnl',
        'Комиссия': 'commission',
        'Комментарий': 'comment',
        'Эмоциональное состояние': 'emotional_state'
    })

    df = df.drop(
        columns=['Итог в пунктах', 'Шаг цены', 'Стоимость шага', 'Биржевые сборы', 'Чистая прибыль/ убыток в usdt.',
                 'Размер депозита до входа в сделку', 'Прибыль/ убыток (в %)', 'Unnamed: 23',
                 'Успешность сделок (с нахождения стиля торговли)'])

    # Ensure 'date' column is in datetime format with correct format and dayfirst
    # Function to convert time strings to datetime.time objects
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y', dayfirst=True, errors='coerce')

    # Function to convert time strings to datetime.time objects
    def parse_time(t):
        if pd.notnull(t):
            if isinstance(t, time):
                return t
            return datetime.strptime(t, '%H:%M:%S').time()
        return None

    # Apply the function to the 'time' column
    df['time'] = df['time'].apply(parse_time)

    # Create a new 'datetime' column, handling NaT in the 'date' column
    df['date_time'] = df.apply(
        lambda row: datetime.combine(row['date'], row['time']) if pd.notnull(row['time']) and pd.notnull(
            row['date']) else row['date'], axis=1)

    df = df.drop(columns=['time', 'date'])

    df['commission'] = df['commission'].fillna(0)

    df = df.set_index('trade_id')

    df.to_csv('df.csv')