from sqlalchemy import create_engine, ForeignKey, Table, Column, String, Integer, CHAR, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import pandas as pd


def get_tool_id(tool_name, db_session):
    return db_session.query(Tool).filter_by(tool_name=tool_name).first().tool_id


def csv_to_sql(csv_file, db_session):
    df = pd.read_csv(csv_file)

    for tool in set(df['tool']):
        db_session.add(Tool(tool))

    db_session.commit()

    dicts = df.to_dict(orient='records')

    for d in dicts:
        tool_id = db_session.query(Tool).filter_by(tool_name=d['tool']).first().tool_id
        trade = Trade(
            tool_id=tool_id,
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

    db_session.commit()


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
    __tablename__ = 'journal'

    trade_id = Column(Integer, primary_key=True, autoincrement=True)
    tool_id = Column(Integer, ForeignKey('tools.tool_id'), nullable=False)
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

    def __init__(self, tool_id, side, price_of_entry, volume, risk_usd, tags=None, date_time=None, reason_of_entry=None,
                 price_of_exit=None, reason_of_exit=None, pnl_usdt=None, commission=None, comment=None,
                 emotional_state=None):
        self.tool_id = tool_id
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

    def __repr__(self):
        return (
            f"<Trade(trade_id={self.trade_id}, tool_id={self.tool_id}, side={self.side}, price_of_entry={self.price_of_entry}, "
            f"volume={self.volume}, risk_usd={self.risk_usd}, tags={self.tags}, date_time={self.date_time}, "
            f"reason_of_entry={self.reason_of_entry}, price_of_exit={self.price_of_exit}, reason_of_exit={self.reason_of_exit}, "
            f"pnl_usdt={self.pnl_usdt}, commission={self.commission}, comment={self.comment}, emotional_state={self.emotional_state})>")


if __name__ == '__main__':
    engine = create_engine("sqlite:///trading.db", echo=True)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    #session.commit()
