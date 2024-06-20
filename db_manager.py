from db_creator import (Account, Trade)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


class DBInterface:
    def __init__(self, account_name, echo=False, ):
        self.account_name = account_name

        engine = create_engine("sqlite:///trading.db", echo=echo)

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

        self.session.commit()

    def update_risk(self, new_risk):
        account = self._get_account_row()

        account.risk = new_risk

        self.session.commit()

    def insert_new_trade(self, **kwargs):
        """
        Insert new trade record into the database. All params are OBLIGATORY

        Parameters:
        - tool (str): Name of the tool.
        - side (str): The side of the trade (e.g., "лонг" or "шорт").
        - risk_usd (float): The risk amount in USD.

        Returns:
        trade_id (int)
        """
        trade = Trade(**kwargs)

        self.session.add(trade)

    def update_trade(self, trade_id, **kwargs):
        """
        Update a trade record with the given trade_id using the provided keyword arguments. All parameters are OPTIONAL.

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
                        setattr(trade, k, v)
                    else:
                        print(f"Trade does not have attribute '{k}'")
            self.session.commit()
        else:
            print(f"Trade with trade_id: {trade_id} does not exist")


