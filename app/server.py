import base64
import threading
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.db_manager import DBInterface
from app import runtime_manager as rm
from app import bingx_exc as be
from app.listener import OrderListener, PriceListener

app = FastAPI()

# Get the absolute path for the templates and static directories
base_path = Path(__file__).parent
templates_path = base_path / "templates"
static_path = base_path / "static"

# Create a Jinja2 templates object
templates = Jinja2Templates(directory=str(templates_path))

# Mount the static files directory
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

db_interface = DBInterface("BingX")

# Dictionary for storing price listeners
listeners_threads = {}


def create_price_listener_for_tool(tool):
    p_listener = PriceListener(tool)

    price_listener_thread = threading.Thread(target=p_listener.listen_for_events)
    price_listener_thread.start()

    listeners_threads[tool] = [price_listener_thread, p_listener]


def delete_price_listener_for_tool(tool):
    try:
        thread, listener = listeners_threads[tool]
        listener.stop_listening()
        thread.join()

        del listeners_threads[tool]
    except Exception as e:
        print("Price listener already deleted")


@app.post("/stop-price-listener/")
def stop_price_listener(cancel_data: dict):
    delete_price_listener_for_tool(cancel_data['tool'])


class AccountUpdateData(BaseModel):
    risk: float
    deposit: float


@app.put("/update-account-data/")
def update_risk(account_update: AccountUpdateData):
    try:
        db_interface.update_risk(account_update.risk)
        db_interface.update_deposit(account_update.deposit)
    except Exception as e:
        print(e)
        return {"message": "Failed to update account data"}
    return {"message": "Account data updated successfully"}


class ToolRequestData(BaseModel):
    tool: str
    long_side: bool


@app.post("/set-default-leverage/")
def set_default_leverage(request: ToolRequestData):
    max_leverage_long, max_leverage_short = be.get_max_leverage(request.tool + "-USDT")
    max_leverage = max_leverage_long if request.long_side else max_leverage_short
    #print(max_leverage)
    return {"max_leverage": max_leverage}


class TradeData(BaseModel):
    tool: str
    entry_p: float
    stop_p: float
    leverage: int
    take_ps: List[float]
    stoe: int
    volume: float


@app.post("/process-trade-data/")
def process_takes(data: TradeData):
    tool = data.tool + "-USDT"
    entry_p = data.entry_p
    stop_p = data.stop_p
    leverage = data.leverage
    take_ps = data.take_ps
    stoe = data.stoe
    volume = data.volume

    #print("Received data:", data.model_dump())

    if volume == 0.0:
        volume, margin = be.calc_position_volume_and_margin(tool, entry_p, stop_p, leverage)
        pot_loss, pot_profit = be.calculate_position_potential_loss_and_profit(tool, entry_p, stop_p, take_ps, volume)
    else:
        margin = volume * entry_p / leverage
        pot_loss, pot_profit = be.calculate_position_potential_loss_and_profit(tool, entry_p, stop_p, take_ps, volume)

    d = {"message": "Data processed successfully", "volume": volume, "margin": margin,
         "potential_loss": pot_loss, "potential_profit": pot_profit}

    #print(d)

    return {"message": "Data processed successfully", "volume": volume, "margin": margin,
            "potential_loss": pot_loss, "potential_profit": pot_profit}


class TradeUpdateData(BaseModel):
    trade_id: int
    field: str
    value: str


@app.put("/update-trade/")
def update_trade(trade_update: TradeUpdateData):
    update_data = {trade_update.field: trade_update.value}
    db_interface.update_trade(trade_update.trade_id, **update_data)
    return {"message": "Trade updated successfully"}


class PositionData(BaseModel):
    tool: str
    entryPrice: float
    triggerPrice: float
    stopPrice: float
    takes: List[float]
    volume: float
    leverage: int
    stoe: int


@app.post("/place-trade/")
def place_trade(pos_data: PositionData):
    tool = pos_data.tool + "-USDT"
    trigger_price = pos_data.triggerPrice
    entry_price = pos_data.entryPrice
    stop_price = pos_data.stopPrice
    takes = pos_data.takes
    leverage = pos_data.leverage
    volume = pos_data.volume
    stoe = pos_data.stoe

    #print("Received data for trade placing:", pos_data.model_dump())

    res = be.place_open_order(tool, trigger_price, entry_price, stop_price, takes, stoe, leverage, volume)

    # Creating price listener for cancel tracking if order was placed
    if res == "Primary order placed":
        create_price_listener_for_tool(tool)

    return {"message": res}


@app.post("/cancel-trade/")
def cancel_trade(trade_data: dict):
    tool = trade_data['tool']

    be.cancel_primary_order_for_tool(tool)

    return {"message": "Trade cancelled successfully"}


class CancelPositionLevels(BaseModel):
    tool: str
    over: float
    take: float


@app.post("/update-cancel-levels/")
def update_cancel_levels(cancel_levels: CancelPositionLevels):
    tool = cancel_levels.tool
    over = cancel_levels.over
    take = cancel_levels.take

    rm.update_info_for_position(tool, cancel_levels=[over, take])

    return {"message": "Cancel levels setup successfully"}


class CommentUpdateData(BaseModel):
    tool: str
    comment: str


@app.post("/update-comment/")
def update_comment(comment_info: CommentUpdateData):
    tool = comment_info.tool.replace("-USDT", "")
    comment = comment_info.comment

    db_interface.update_last_trade_of_tool(tool, comment=comment)


class EmotionalStateUpdateData(BaseModel):
    tool: str
    emotional_state: str


@app.post("/update-emotional-state/")
def update_comment(emotional_state_info: EmotionalStateUpdateData):
    tool = emotional_state_info.tool.replace("-USDT", "")
    emotional_state = emotional_state_info.emotional_state

    db_interface.update_last_trade_of_tool(tool, emotional_state=emotional_state)


@app.get('/get-trade-images/{trade_id}')
def get_trade_images(trade_id: int):
    info = db_interface.get_info_for_trade(trade_id, ['screen', 'screen_zoomed'])

    if info is not None:
        screen = base64.b64encode(info[0]).decode('utf-8') if info[0] else None
        screen_zoomed = base64.b64encode(info[1]).decode('utf-8') if info[1] else None

        return {
            "screen": screen,  # Assuming you store the image path or base64 encoded string
            "screen_zoomed": screen_zoomed
        }
    else:
        return {"screen": None, "screen_zoomed": None}


@app.post("/update-trade-screens/")
async def update_trade_screens(
        trade_id: int = Form(...),
        screen: Optional[UploadFile] = File(None),
        screen_zoomed: Optional[UploadFile] = File(None),
):
    screen_data = await screen.read() if screen else None
    screen_zoomed_data = await screen_zoomed.read() if screen_zoomed else None

    try:
        db_interface.update_trade(trade_id, screen=screen_data, screen_zoomed=screen_zoomed_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Trade updated successfully"}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    deposit, risk, unrealized_pnl, available_margin = be.get_account_details()

    tools = db_interface.get_all_tools()
    curr_positions = be.get_current_positions_info()
    pend_positions = be.get_pending_positions_info()

    return templates.TemplateResponse("index.html",
                                      {
                                          "request": request,
                                          "deposit": deposit,
                                          "risk": risk,
                                          "unrealized_pnl": unrealized_pnl,
                                          "available_margin": available_margin,
                                          "tools": tools,
                                          "current_positions": curr_positions,
                                          "pending_positions": pend_positions
                                      }
                                      )


@app.get("/journal", response_class=HTMLResponse)
async def read_journal(request: Request):
    trades = db_interface.get_all_trades()
    return templates.TemplateResponse("journal.html", {"request": request, "trades": trades})


def start_listener():
    listener = OrderListener()
    listener.listen_for_events()


# Starting orders listener
listener_thread = threading.Thread(target=start_listener)
listener_thread.start()
