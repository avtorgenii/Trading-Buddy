from sqlalchemy import create_engine, ForeignKey, Table, Column, String, Integer, CHAR, DateTime, Enum, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import enum
import pandas as pd

Base = declarative_base()


class Tool(Base):
    __tablename__ = 'tools'

    tool_id = Column(Integer, primary_key=True, autoincrement=True)
    tool_name = Column(String, nullable=False, unique=True)

    def __init__(self, tool_name):
        self.tool_name = tool_name

    def __repr__(self):
        return f"<Tool(tool_id={self.tool_id}, tool_name={self.tool_name})>"


class Trade(Base):
    class PositionType(enum.Enum):
        LONG = "Long"
        SHORT = "Short"

    __tablename__ = 'journal'

    trade_id = Column(Integer, primary_key=True, autoincrement=True)
    tool_id = Column(Integer, ForeignKey('tools.tool_id'), nullable=False)
    side = Column(Enum(PositionType), nullable=False)
    tags = Column(String)
    date = Column(DateTime)
    reason_of_entry = Column(String)
    price_of_entry = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    price_of_exit = Column(Float)
    reason_of_exit = Column(String)
    risk_usd = Column(Float, nullable=False)
    pnl_usdt = Column(Float)
    commission = Column(Float)
    comment = Column(String)
    emotional_state = Column(String)

    def __init__(self, tool, side, price_of_entry, volume, risk_usd):
        self.tool = tool
        self.side = side
        self.price_of_entry = price_of_entry
        self.volume = volume
        self.risk_usd = risk_usd

    def __repr__(self):
        return (f"<Trade(tid={self.tid}, tool={self.tool}, side={self.side}, "
                f"price_of_entry={self.price_of_entry}, volume={self.volume}, risk_usd={self.risk_usd})>")


# engine = create_engine("sqlite:///trading.db", echo=True)
# Base.metadata.create_all(bind=engine)
#
# Session = sessionmaker(bind=engine)
# session = Session()


if __name__ == '__main__':
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
                 'Размер депозита до входа в сделку', 'Прибыль/ убыток (в %)', 'Unnamed: 22',
                 'Успешность сделок (с нахождения стиля торговли)'])


