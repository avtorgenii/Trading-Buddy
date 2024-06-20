import os.path
from sqlalchemy import create_engine, Table, Column, String, Integer, LargeBinary, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import pandas as pd
from datetime import datetime, time


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
            price_of_entry=d['price_of_entry'],
            volume=d['volume'],
            risk_usd=d['risk_usd'],
            tags=d.get('tags'),
            date_time=pd.to_datetime(d.get('date_time')),
            reason_of_entry=d.get('reason_of_entry'),
            price_of_exit=d.get('price_of_exit'),
            reason_of_exit=d.get('reason_of_exit'),
            pnl_usdt=d.get('pnl'),
            commission=d.get('commission'),
            comment=d.get('comment'),
            emotional_state=d.get('emotional_state')
        )

        db_session.add(trade)

    db_session.add(Account(account_name="BingX", deposit=deposit, risk=risk))

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


class Trade(Base):
    __tablename__ = 'trades'

    trade_id = Column(Integer, primary_key=True, autoincrement=True)
    tool = Column(String, nullable=False)
    side = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    date_time = Column(DateTime, nullable=True)
    reason_of_entry = Column(String, nullable=True)
    price_of_entry = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    price_of_exit = Column(Float, nullable=True)
    reason_of_exit = Column(String, nullable=True)
    risk_usd = Column(Float, nullable=False)
    pnl_usdt = Column(Float, nullable=True)
    commission = Column(Float, nullable=True)
    comment = Column(String, nullable=True)
    emotional_state = Column(String, nullable=True)
    screen = Column(LargeBinary, nullable=True)
    screen_zoomed = Column(LargeBinary, nullable=True)

    def __init__(self, tool, side, price_of_entry, volume, risk_usd, tags=None, date_time=None, reason_of_entry=None,
                 price_of_exit=None, reason_of_exit=None, pnl_usdt=None, commission=None, comment=None,
                 emotional_state=None, screen=None, screen_zoomed=None):
        super().__init__()
        self.tool = tool
        self.side = side
        self.price_of_entry = price_of_entry
        self.volume = volume
        self.risk_usd = risk_usd
        self.tags = tags
        self.date_time = date_time
        self.reason_of_entry = reason_of_entry
        self.price_of_exit = price_of_exit
        self.reason_of_exit = reason_of_exit
        self.pnl_usdt = pnl_usdt
        self.commission = commission
        self.comment = comment
        self.emotional_state = emotional_state
        self.screen = screen
        self.screen_zoomed = screen_zoomed

    def __repr__(self):
        return (
            f"<Trade(trade_id={self.trade_id}, tool_id={self.tool_id}, side={self.side}, price_of_entry={self.price_of_entry},"
            f"volume={self.volume}, risk_usd={self.risk_usd}, tags={self.tags}, date_time={self.date_time}, "
            f"reason_of_entry={self.reason_of_entry}, price_of_exit={self.price_of_exit}, reason_of_exit={self.reason_of_exit},"
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
