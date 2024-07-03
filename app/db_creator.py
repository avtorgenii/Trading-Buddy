import os.path
from sqlalchemy import create_engine, Column, String, Integer, LargeBinary, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

import pandas as pd


from datetime import datetime, time

from app.math_helper import floor_to_digits, convert_to_unix

def excel_to_csv(excel):
    # Load the Excel file
    file_path = 'used/Journal.xlsx'
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


def csv_to_sql(csv_file, db_session, deposit, risk):
    df = pd.read_csv(csv_file)

    dicts = df.to_dict(orient='records')

    for d in dicts:
        trade = Trade(
            tool=d['tool'],
            side=d['side'],
            volume=d['volume'],
            risk_usdt=d['risk_usd'],
            tags=d.get('tags'),
            start_time=convert_to_unix(d['date_time']),
            end_time=None,
            reason_of_entry=d.get('reason_of_entry'),
            reason_of_exit=d.get('reason_of_exit'),
            pnl_usdt=floor_to_digits(d.get('pnl'), 3),
            commission=d.get('commission'),
            comment=d.get('comment'),
            emotional_state=d.get('emotional_state')
        )

        db_session.add(trade)

    db_session.add(Account(account_name="BingX", deposit=deposit, risk=risk))

    tools = ['FTM', 'ADA', 'LINK', 'KAVA', 'ENJ', 'EOS', 'ICX', 'IOTA', 'GMT', 'RUNE']

    for tool in tools:
        db_session.add(Tool(tool_name=tool, starred=True))

    db_session.commit()


def add_screens_to_rows(row_ids, db_session):
    screen_names = [f"{num}.png" for num in row_ids]
    screen_zoomed_names = [f"{num} Z.png" for num in row_ids]

    for row_id, screen_name, screen_zoomed_name in zip(row_ids, screen_names, screen_zoomed_names):
        row = db_session.query(Trade).filter_by(trade_id=row_id).first()
        if row:
            with open(os.path.join(r"C:\Users\ashes\OneDrive\Рабочий стол\Graphic Journal", screen_name), 'rb') as file:
                image_data = file.read()
                row.screen = image_data

            with open(os.path.join(r"C:\Users\ashes\OneDrive\Рабочий стол\Graphic Journal", screen_zoomed_name),
                      'rb') as file:
                image_data = file.read()
                row.screen_zoomed = image_data

            db_session.commit()


Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    account_name = Column(String, nullable=False)
    deposit = Column(Float, nullable=False)
    risk = Column(Float, nullable=False)

    def __init__(self, account_name, deposit, risk):
        super().__init__()
        self.account_name = account_name
        self.deposit = deposit
        self.risk = risk

    def __repr__(self):
        return f"<Account(account_name={self.account_name}, deposit={self.deposit}, risk={self.risk})>"


class Tool(Base):
    __tablename__ = "tools"

    tool_id = Column(Integer, primary_key=True, autoincrement=True)
    tool_name = Column(String, nullable=False, unique=True)
    starred = Column(Boolean, nullable=False)

    def __init__(self, tool_name, starred):
        super().__init__()
        self.tool_name = tool_name
        self.starred = starred

    def __repr__(self):
        return f"<Tool(tool_id={self.tool_id}, tool_name='{self.tool_name}', starred={self.starred})>"


class Trade(Base):
    __tablename__ = 'trades'

    trade_id = Column(Integer, primary_key=True, autoincrement=True)
    tool = Column(String, nullable=False)
    side = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    start_time = Column(Integer, nullable=True)
    end_time = Column(Integer, nullable=True)
    reason_of_entry = Column(String, nullable=True)
    volume = Column(Float, nullable=True)
    reason_of_exit = Column(String, nullable=True)
    risk_usdt = Column(Float, nullable=True)
    pnl_usdt = Column(Float, nullable=True)
    commission = Column(Float, nullable=True)
    comment = Column(String, nullable=True)
    emotional_state = Column(String, nullable=True)
    screen = Column(LargeBinary, nullable=True)
    screen_zoomed = Column(LargeBinary, nullable=True)

    def __init__(self, tool, side, start_time=None, end_time=None, volume=None, risk_usdt=None, tags=None,
                 reason_of_entry=None, reason_of_exit=None, pnl_usdt=None, commission=None, comment=None,
                 emotional_state=None, screen=None, screen_zoomed=None):
        super().__init__()
        self.tool = tool
        self.side = side
        self.volume = volume
        self.risk_usdt = risk_usdt
        self.tags = tags
        self.start_time = start_time
        self.end_time = end_time
        self.reason_of_entry = reason_of_entry
        self.reason_of_exit = reason_of_exit
        self.pnl_usdt = pnl_usdt
        self.commission = commission
        self.comment = comment
        self.emotional_state = emotional_state
        self.screen = screen
        self.screen_zoomed = screen_zoomed

    def __repr__(self):
        utc_start = self.start_time
        utc_end = self.end_time
        return (
            f"<Trade(trade_id={self.trade_id}, tool={self.tool}, side={self.side}, start_time={utc_start}, end_time={utc_end}"
            f"volume={self.volume}, risk_usdt={self.risk_usdt}, tags={self.tags}, "
            f"reason_of_entry={self.reason_of_entry}, reason_of_exit={self.reason_of_exit},"
            f"pnl_usdt={self.pnl_usdt}, commission={self.commission}, comment={self.comment}, emotional_state={self.emotional_state})>")


def create_db(echo=False):
    """
    Delete .db file before firing this func
    """
    engine = create_engine("sqlite:///trading.db", echo=echo)

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    csv_to_sql("used/df.csv", session, 90.34, 3)

    add_screens_to_rows(range(137, 147), session)

    session.commit()


if __name__ == '__main__':
    create_db()
