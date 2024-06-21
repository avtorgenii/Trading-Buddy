from typing import List

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from db_manager import DBInterface
import bingx_exc as be

app = FastAPI()

# Create a Jinja2 templates object
templates = Jinja2Templates(directory="templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

db_interface = DBInterface("BingX")


# Define the RiskUpdate model
class RiskUpdate(BaseModel):
    risk: float


@app.put("/update-risk/")
def update_risk(risk_update: RiskUpdate):
    db_interface.update_risk(risk_update.risk)

    print(risk_update.risk)

    return {"message": "Risk updated successfully", "risk": risk_update.risk}


class ToolRequest(BaseModel):
    tool: str
    long_side: bool


@app.post("/set-default-leverage/")
def set_default_leverage(request: ToolRequest):
    max_leverage_long, max_leverage_short = be.get_max_leverage(request.tool + "-USDT")

    max_leverage = max_leverage_long if request.long_side else max_leverage_short

    print(max_leverage)

    return {"max_leverage": max_leverage}


class TradeData(BaseModel):
    tool: str
    entry_p: float
    stop_p: float
    leverage: int
    take_ps: List[float]
    stoe: int


@app.post("/process-trade-data/")
def process_takes(data: TradeData):
    tool = data.tool + "-USDT"
    entry_p = data.entry_p
    stop_p = data.stop_p
    leverage = data.leverage
    take_ps = data.take_ps
    stoe = data.stoe

    print("Received data:", data.model_dump())

    volume, margin = be.calc_position_volume_and_margin(tool, entry_p, stop_p, leverage)

    pot_loss, pot_profit = be.calculate_position_potential_loss_and_profit(tool, entry_p, stop_p, take_ps, volume)

    d = {"message": "Data processed successfully", "volume": volume, "margin": margin,
         "potential_loss": pot_loss, "potential_profit": pot_profit}

    print(d)

    return {"message": "Data processed successfully", "volume": volume, "margin": margin,
            "potential_loss": pot_loss, "potential_profit": pot_profit}


class TradeUpdate(BaseModel):
    trade_id: int
    field: str
    value: str


@app.put("/update-trade/")
def update_trade(trade_update: TradeUpdate):
    update_data = {trade_update.field: trade_update.value}
    db_interface.update_trade(trade_update.trade_id, **update_data)
    return {"message": "Trade updated successfully"}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    deposit, risk, unrealized_pnl, available_margin = be.get_account_details()

    tools = db_interface.get_all_tools()

    return templates.TemplateResponse("index.html",
                                      {
                                          "request": request,
                                          "deposit": deposit,
                                          "risk": risk,
                                          "unrealized_pnl": unrealized_pnl,
                                          "available_margin": available_margin,
                                          "tools": tools
                                      }
                                      )


@app.get("/journal", response_class=HTMLResponse)
async def read_journal(request: Request):
    trades = db_interface.get_all_trades()
    return templates.TemplateResponse("journal.html", {"request": request, "trades": trades})
