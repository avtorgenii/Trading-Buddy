import os

from db_creator import (Account, Trade)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


class DBInterface:
    def __init__(self, account_name, echo=False, ):
        self.account_name = account_name

        engine = create_engine("sqlite:///trading.db", echo=echo)

        if not os.path.exists("trading.db"):
            Base = declarative_base()
            Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)

        self.session = Session()

    def _get_account_row(self):
        return self.session.query(Account).filter_by(account_name=self.account_name).first()

    def get_account_details(self):
        account = self._get_account_row()

        return account.deposit, account.risk

    def update_deposit(self, new_deposit):
        account = self._get_account_row()

        account.deposit = new_deposit

    def update_risk(self, new_risk):
        account = self._get_account_row()

        account.risk = new_risk

    def insert_new_trade(self, tool, entry_p, ):
        trade = Trade(tool, entry_p, )

        self.session.add(trade)

        self.session.commit()

        return trade.trade_id


    def update_trade(self, trade_id):
        trade = self.session.query(Trade).filter_by(trade_id=trade_id).first()

        if trade is not None:
            trade. =
        else:
            print(f"Trade of trade_id: {trade_id} does not exist")