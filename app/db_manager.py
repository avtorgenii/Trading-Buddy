import os
from datetime import datetime
from typing import List

from app.db_creator import (Account, Trade, Tool)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


class DBInterface:
    def __init__(self, account_name, echo=False):
        self.account_name = account_name

        DATABASE_URL = os.path.join(os.path.dirname(__file__), 'trading.db')
        engine = create_engine(f"sqlite:///{DATABASE_URL}", echo=echo)

        Base = declarative_base()
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)

        self.session = Session()

    def __del__(self):
        self.session.close()

    def _get_account_row(self):
        return self.session.query(Account).filter_by(account_name=self.account_name).first()

    def get_account_details(self):
        account = self._get_account_row()

        return account.deposit, account.risk

    def update_deposit(self, new_deposit):
        account = self._get_account_row()

        account.deposit = new_deposit

        self.session.commit()

    def update_risk(self, new_risk):
        account = self._get_account_row()

        account.risk = new_risk

        self.session.commit()

    def get_all_tools(self):
        return [tool.tool_name for tool in self.session.query(Tool).all()]

    def get_all_trades(self):
        return self.session.query(Trade).order_by(Trade.trade_id.desc()).all()

    def insert_new_trade(self, **kwargs):
        """
        Insert new trade record into the database. All params are OBLIGATORY

        Parameters:
        - tool (str): Name of the tool.
        - side (str): The side of the trade (e.g., "лонг" or "шорт").
        - risk_usdt (float): Potential loss of a trade
        """
        trade = Trade(**kwargs)

        self.session.add(trade)
        self.session.commit()

    def remove_last_trade_of_tool(self, tool):
        last_trade = self.session.query(Trade).filter_by(tool=tool).order_by(Trade.trade_id.desc()).first()

        if last_trade:
            self.session.delete(last_trade)
            self.session.commit()

    def get_info_for_trade(self, trade_id, params: List[str]):
        """
        Retrieves specific information for a trade with the given trade_id.

        Parameters:
         - trade_id (int): The ID of the trade to retrieve.
        - params (List[str]): The list of fields to retrieve.

        Returns:
        - list: A list containing the requested values for fields
        """
        trade = self.session.query(Trade).filter_by(trade_id=trade_id).first()

        if not trade:
            print(f"Trade with trade_id: {trade_id} does not exist")
            return None

        trade_info = []
        for param in params:
            if hasattr(trade, param):
                trade_info.append(getattr(trade, param))
            else:
                print(f"Trade does not have attribute '{param}'")

        return trade_info

    def update_last_trade_of_tool(self, tool, **kwargs):
        """
        Updates LAST row of a given tool with the provided keyword arguments. All parameters are OPTIONAL.

        DO NOT PASS ANY OTHER PARAMS EXCEPT ONES BELOW

        Parameters:
        - trade_id (int): The ID of the trade to update.
        - tags (str): Tags associated with the trade.
        - date_time (datetime): The date and time of the trade.
        - reason_of_entry (str): The reason for entering the trade.
        - price_of_entry (float): The entry price of the trade.
        - volume (float): The volume of the trade.
        - price_of_exit (float): The exit price of the trade.
        - reason_of_exit (str): The reason for exiting the trade.
        - pnl_usdt (float): The profit and loss in USDT.
        - commission (float): The commission for the trade.
        - comment (str): Comments on the trade.
        - emotional_state (str): The emotional state before the trade.
        - screen (bytes): The screenshot of the trade.
        - screen_zoomed (bytes): The zoomed screenshot of the trade.

        Returns:
        None
        """
        trade = self.session.query(Trade).filter_by(tool=tool).order_by(Trade.trade_id.desc()).first()

        if trade is not None:
            for k, v in kwargs.items():
                if v is not None:
                    if hasattr(trade, k):
                        setattr(trade, k, v)
                    else:
                        print(f"Trade does not have attribute '{k}'")
            self.session.commit()
        else:
            print(f"Trade for tool: {tool} does not exist")

    def update_trade(self, trade_id, **kwargs):
        """
        Updates row with given trade_id using the provided keyword arguments. All parameters are OPTIONAL.

        DO NOT PASS ANY OTHER PARAMS EXCEPT ONES BELOW

        Parameters:
        - trade_id (int): The ID of the trade to update.
        - tags (str): Tags associated with the trade.
        - date_time (datetime): The date and time of the trade.
        - reason_of_entry (str): The reason for entering the trade.
        - price_of_entry (float): The entry price of the trade.
        - volume (float): The volume of the trade.
        - price_of_exit (float): The exit price of the trade.
        - reason_of_exit (str): The reason for exiting the trade.
        - pnl_usdt (float): The profit and loss in USDT.
        - commission (float): The commission for the trade.
        - comment (str): Comments on the trade.
        - emotional_state (str): The emotional state before the trade.
        - screen (bytes): The screenshot of the trade.
        - screen_zoomed (bytes): The zoomed screenshot of the trade.

        Returns:
        None
        """
        trade = self.session.query(Trade).filter_by(trade_id=trade_id).first()

        if trade is not None:
            for k, v in kwargs.items():
                if v is not None:
                    if hasattr(trade, k):
                        casted_value = self._cast_value_to_field_type(trade, k, v)
                        setattr(trade, k, casted_value)
                    else:
                        print(f"Trade does not have attribute '{k}'")
            self.session.commit()
        else:
            print(f"Trade of trade_id: {trade_id} does not exist")

    def _cast_value_to_field_type(self, trade, field, value):
        field_type = type(getattr(trade, field))
        if field_type == int:
            return int(value)
        elif field_type == float:
            return float(value)
        elif field_type == datetime:
            return datetime.fromisoformat(value)
        else:
            return value
