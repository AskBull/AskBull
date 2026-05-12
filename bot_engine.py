"""
AskBull PSX Bot Engine
Built from Final_version_Psx_day_trader.ipynb
Exact same stock universe, CONFIG, weights and AUTO_PCT targeting.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import ta
from datetime import datetime
import pytz

warnings.filterwarnings("ignore")
PST = pytz.timezone("Asia/Karachi")

# ─── MASTER CONFIG (exact copy from your notebook) ────────────────────────
CONFIG = {
    "STOCK_UNIVERSE": [
        "HBL.KA","UBL.KA","MCB.KA","BAFL.KA","MEBL.KA","NBP.KA","BAHL.KA","AKBL.KA",
        "LUCK.KA","DGKC.KA","MLCF.KA","CHCC.KA","FCCL.KA","PIOC.KA","KOHC.KA",
        "ENGRO.KA","EFERT.KA","FFBL.KA","FFC.KA","FATIMA.KA",
        "PSO.KA","SHEL.KA","APL.KA","HASCOL.KA","PPL.KA","OGDC.KA","POL.KA","MARI.KA",
        "HUBC.KA","KAPCO.KA","NCPL.KA","PKGP.KA",
        "PSMC.KA","INDU.KA","HCAR.KA","MTL.KA",
        "PAEL.KA","AVN.KA","SYS.KA","TRG.KA","NETSOL.KA",
        "COLG.KA","NESTLE.KA","UNILEVER.KA","ICI.KA",
        "GATM.KA","NML.KA","NCL.KA","KTML.KA",
        "AGTL.KA","ASTL.KA","ISL.KA","MUGHAL.KA",
        "SEARL.KA","GLAXO.KA","FEROZ.KA","HINOON.KA","ABOT.KA",
        "SNGP.KA","SSGC.KA",
        "WTL.KA","PTCL.KA","CNERGY.KA",
        "PNSC.KA","LOTCHEM.KA","EPCL.KA","SITC.KA",
    ],
    "RSI_PERIOD": 14,
    "RSI_OVERSOLD": 35,
    "RSI_OVERBOUGHT": 65,
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    "BB_PERIOD": 20,
    "BB_STD": 2,
    "SMA_SHORT": 10,
    "SMA_MEDIUM": 20,
    "SMA_LONG": 50,
    "EMA_SHORT": 9,
    "EMA_MEDIUM": 21,
    "ATR_PERIOD": 14,
    "ADX_PERIOD": 14,
    "ADX_TREND_THRESHOLD": 25,
    "STOCH_K": 14,
    "STOCH_D": 3,
    "VOLUME_MA_PERIOD": 20,
    "VOLUME_SPIKE_MULTIPLIER": 1.5,
    "WEIGHTS": {
        "technical":   0.45,
        "momentum":    0.20,
        "volume":      0.15,
        "sentiment":   0.10,
        "fundamental": 0.10,
    },
    "HISTORY_PERIOD": "6mo",
    "TOP_N_STOCKS": 5,
    "ATR_SL_MULT": 1.0,
    "ATR_T1_MULT": 0.6,
    "ATR_T2_MULT": 1.1,
    "MAX_INTRADAY_TARGET_PCT": 3.5,
    "CAP_T1_AT_RESISTANCE": True,
    "STRATEGY": {
        "MODE": "AUTO_PCT",
        "TARGET_T1_PCT": 1.0,
        "TARGET_T2_PCT": 2.0,
        "STOP_LOSS_PCT": 1.0,
        "AUTO_T1_PERCENTILE": 40,
        "AUTO_T2_PERCENTILE": 65,
        "AUTO_SL_PERCENTILE": 35,
    },
}

STOCK_NAMES = {
    "HBL.KA":"Habib Bank","UBL.KA":"United Bank","MCB.KA":"MCB Bank",
    "BAFL.KA":"Bank Alfalah","MEBL.KA":"Meezan Bank","NBP.KA":"National Bank",
    "BAHL.KA":"Bank Al-Habib","AKBL.KA":"Askari Bank",
    "LUCK.KA":"Lucky Cement","DGKC.KA":"DG Khan Cement","MLCF.KA":"Maple Leaf Cement",
    "CHCC.KA":"Cherat Cement","FCCL.KA":"Fauji Cement","PIOC.KA":"Pioneer Cement",
    "KOHC.KA":"Kohat Cement",
    "ENGRO.KA":"Engro Corp","EFERT.KA":"Engro Fertilizers","FFBL.KA":"Fauji Fert BQ",
    "FFC.KA":"Fauji Fertilizer","FATIMA.KA":"Fatima Fertilizer",
    "PSO.KA":"Pakistan State Oil","SHEL.KA":"Shell Pakistan","APL.KA":"Attock Petroleum",
    "HASCOL.KA":"Hascol Petroleum","PPL.KA":"Pakistan Petroleum",
    "OGDC.KA":"Oil & Gas Dev","POL.KA":"Pakistan Oilfields","MARI.KA":"Mari Petroleum",
    "HUBC.KA":"Hub Power","KAPCO.KA":"Kot Addu Power","NCPL.KA":"Nishat Chunian Power",
    "PKGP.KA":"PakGen Power",
    "PSMC.KA":"Pak Suzuki","INDU.KA":"Indus Motor","HCAR.KA":"Honda Atlas",
    "MTL.KA":"Millat Tractors",
    "PAEL.KA":"Pak Elektron","AVN.KA":"Avanceon","SYS.KA":"Systems Ltd",
    "TRG.KA":"TRG Pakistan","NETSOL.KA":"NetSol Tech",
    "COLG.KA":"Colgate Pakistan","NESTLE.KA":"Nestle Pakistan",
    "UNILEVER.KA":"Unilever Pakistan","ICI.KA":"ICI Pakistan",
    "GATM.KA":"Gul Ahmed Textile","NML.KA":"Nishat Mills","NCL.KA":"Nishat Chunian",
    "KTML.KA":"Kohinoor Textile",
    "AGTL.KA":"Al-Ghazi Tractors","ASTL.KA":"Agha Steel",
    "ISL.KA":"International Steel","MUGHAL.KA":"Mughal Steel",
    "SEARL.KA":"Searle Pakistan","GLAXO.KA":"GlaxoSmithKline",
    "FEROZ.KA":"Ferozsons Labs","HINOON.KA":"Highnoon Labs","ABOT.KA":"Abbott Labs",
    "SNGP.KA":"Sui Northern Gas","SSGC.KA":"Sui Southern Gas",
    "WTL.KA":"WorldCall Telecom","PTCL.KA":"PTCL","CNERGY.KA":"Cnergyico PK",
    "PNSC.KA":"Pak National Ship","LOTCHEM.KA":"LOTChem",
    "EPCL.KA":"EPCL","SITC.KA":"Sitara Chemical",
}


# ─── Data Fetcher ─────────────────────────────────────────────────────────
class PSXDataFetcher:
    def __init__(self):
        self._cache = {}

    def fetch(self, ticker: str):
        if ticker in self._cache:
            return self._cache[ticker]
        try:
            df = yf.download(ticker, period=CONFIG["HISTORY_PERIOD"],
                             auto_adjust=True, progress=False, multi_level_index=False)
            if df is None or df.empty or len(df) < 50:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0].lower() for c in df.columns]
            else:
                df.columns = [str(c).lower() for c in df.columns]
            df = df.loc[:, ~df.columns.duplicated()]
            df.index = pd.to_datetime(df.index)
            self._cache[ticker] = df
            return df
        except Exception:
            return None


# ─── Technical Analyzer ───────────────────────────────────────────────────
class TechnicalAnalyzer:
    def compute_all(self, df: pd.DataFrame):
        if df is None or len(df) < 50:
            return None
        df = df.copy()
        close = df["close"]
        high  = df["high"]
        low   = df["low"]
        vol   = df["volume"]

        df["sma10"]  = ta.trend.sma_indicator(close, 10)
        df["sma20"]  = ta.trend.sma_indicator(close, 20)
        df["sma50"]  = ta.trend.sma_indicator(close, 50)
        df["ema9"]   = ta.trend.ema_indicator(close, 9)
        df["ema21"]  = ta.trend.ema_indicator(close, 21)

        macd_obj       = ta.trend.MACD(close, 12, 26, 9)
        df["macd"]     = macd_obj.macd()
        df["macd_sig"] = macd_obj.macd_signal()
        df["macd_hist"]= macd_obj.macd_diff()

        adx_obj        = ta.trend.ADXIndicator(high, low, close, 14)
        df["adx"]      = adx_obj.adx()
        df["adx_pos"]  = adx_obj.adx_pos()
        df["adx_neg"]  = adx_obj.adx_neg()

        df["rsi"]      = ta.momentum.RSIIndicator(close, 14).rsi()
        stoch          = ta.momentum.StochasticOscillator(high, low, close, 14, 3)
        df["stoch_k"]  = stoch.stoch()
        df["stoch_d"]  = stoch.stoch_signal()

        bb             = ta.volatility.BollingerBands(close, 20, 2)
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_mid"]   = bb.bollinger_mavg()
        df["bb_lower"] = bb.bollinger_lband()
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"].replace(0, np.nan)
        df["atr"]      = ta.volatility.AverageTrueRange(high, low, close, 14).average_true_range()

        df["obv"]      = ta.volume.OnBalanceVolumeIndicator(close, vol).on_balance_volume()
        df["vol_ma"]   = vol.rolling(20).mean()
        df["vol_ratio"]= vol / df["vol_ma"].replace(0, np.nan)
        df["mfi"]      = ta.volume.MFIIndicator(high, low, close, vol, 14).money_flow_index()

        row  = df.iloc[-1]
        prev = df.iloc[-2]

        def safe(v, default=0.0):
            try:
                f = float(v)
                return f if not np.isnan(f) else default
            except Exception:
                return default

        score   = 50.0
        signals = []

        rsi     = safe(row["rsi"], 50)
        price   = safe(close.iloc[-1], 0)
        sma20   = safe(row["sma20"],  price)
        sma50   = safe(row["sma50"],  price)
        ema9    = safe(row["ema9"],   price)
        ema21   = safe(row["ema21"],  price)
        hist    = safe(row["macd_hist"])
        p_hist  = safe(prev["macd_hist"])
        adx     = safe(row["adx"])
        adx_pos = safe(row["adx_pos"])
        adx_neg = safe(row["adx_neg"])
        bb_width= safe(row["bb_width"])
        bb_lower= safe(row["bb_lower"])
        bb_upper= safe(row["bb_upper"])
        vol_ratio=safe(row["vol_ratio"], 1.0)
        stoch_k = safe(row["stoch_k"], 50)
        stoch_d = safe(row["stoch_d"], 50)
        atr     = safe(row["atr"])
        mfi     = safe(row["mfi"], 50)

        # RSI
        if rsi < CONFIG["RSI_OVERSOLD"]:
            score += 15; signals.append(f"RSI oversold ({rsi:.0f})")
        elif rsi < 45:
            score += 8;  signals.append(f"RSI low ({rsi:.0f})")
        elif rsi > CONFIG["RSI_OVERBOUGHT"]:
            score -= 15; signals.append(f"RSI overbought ({rsi:.0f})")
        elif rsi > 55:
            score -= 5

        # Trend
        if price > sma20 > sma50:
            score += 12; signals.append("Above SMA20 > SMA50 (uptrend)")
        elif price < sma20 < sma50:
            score -= 12; signals.append("Below SMA20 < SMA50 (downtrend)")
        if ema9 > ema21:
            score += 8;  signals.append("EMA9 > EMA21 bullish stack")
        else:
            score -= 5

        # MACD
        if hist > 0 and p_hist <= 0:
            score += 15; signals.append("MACD bullish crossover")
        elif hist > 0:
            score += 7;  signals.append("MACD positive histogram")
        elif hist < 0 and p_hist >= 0:
            score -= 15; signals.append("MACD bearish crossover")
        elif hist < 0:
            score -= 5

        # ADX
        if adx > CONFIG["ADX_TREND_THRESHOLD"]:
            if adx_pos > adx_neg:
                score += 8; signals.append(f"ADX {adx:.0f} strong uptrend")
            else:
                score -= 8; signals.append(f"ADX {adx:.0f} strong downtrend")

        # Bollinger
        if bb_width < 0.04:
            score += 5;  signals.append("BB squeeze — breakout pending")
        if price <= bb_lower:
            score += 10; signals.append("Price at BB lower band (oversold)")
        elif price >= bb_upper:
            score -= 10; signals.append("Price at BB upper band (overbought)")

        # Volume
        if vol_ratio >= CONFIG["VOLUME_SPIKE_MULTIPLIER"]:
            score += 8; signals.append(f"Volume spike {vol_ratio:.1f}x average")
        elif vol_ratio < 0.5:
            score -= 3

        # Stochastic
        if stoch_k < 20 and stoch_k > stoch_d:
            score += 8;  signals.append("Stochastic oversold bullish cross")
        elif stoch_k > 80 and stoch_k < stoch_d:
            score -= 8;  signals.append("Stochastic overbought bearish cross")

        # OBV trend confirmation
        obv_trend = float(df["obv"].diff(5).iloc[-1]) if "obv" in df.columns else 0
        if obv_trend > 0 and price > sma20:
            score += 5; signals.append("OBV rising with price (confirmed)")
        elif obv_trend < 0 and price < sma20:
            score -= 5

        score = min(max(score, 0), 100)

        return {
            "technical_score": round(score, 1),
            "signals":   signals,
            "rsi":       round(rsi, 1),
            "macd_hist": round(hist, 4),
            "adx":       round(adx, 1),
            "atr":       round(atr, 2),
            "bb_width":  round(bb_width, 4),
            "vol_ratio": round(vol_ratio, 2),
            "stoch_k":   round(stoch_k, 1),
            "mfi":       round(mfi, 1),
            "price":     round(price, 2),
            "sma20":     round(sma20, 2),
            "sma50":     round(sma50, 2),
            "ema9":      round(ema9, 2),
            "bb_upper":  round(bb_upper, 2),
            "bb_lower":  round(bb_lower, 2),
            "df":        df,
        }


# ─── Market Context ───────────────────────────────────────────────────────
class MarketContextAnalyzer:
    def get_regime(self) -> dict:
        regime = {"regime": "NEUTRAL", "multiplier": 1.0, "details": []}
        try:
            df = yf.download("^KSE100", period="3mo", auto_adjust=True, progress=False)
            if df.empty:
                return regime
            df.columns = [c.lower() for c in df.columns]
            close = df["close"]
            sma20 = float(close.rolling(20).mean().iloc[-1])
            sma50 = float(close.rolling(50).mean().iloc[-1])
            last  = float(close.iloc[-1])
            if last > sma20 > sma50:
                regime.update({"regime": "BULLISH", "multiplier": 1.15})
                regime["details"].append("KSE-100 uptrend — all clear")
            elif last < sma20 < sma50:
                regime.update({"regime": "BEARISH", "multiplier": 0.85})
                regime["details"].append("KSE-100 downtrend — be cautious")
            else:
                regime["details"].append("KSE-100 mixed — select carefully")
            d5 = float(close.pct_change(5).iloc[-1] * 100)
            if d5 < -2:
                regime["multiplier"] *= 0.9
                regime["details"].append(f"KSE-100 5d: {d5:.1f}% weakness")
            elif d5 > 1:
                regime["details"].append(f"KSE-100 5d: +{d5:.1f}% momentum")
        except Exception:
            pass
        return regime


# ─── Master Scorer ────────────────────────────────────────────────────────
class MasterScorer:
    def score(self, technical_score, vol_ratio, market_mult) -> dict:
        w = CONFIG["WEIGHTS"]
        momentum_score    = min(max((technical_score - 50) * 1.5 + 50, 0), 100)
        volume_score      = min(max((vol_ratio - 1) * 40 + 50, 0), 100)
        sentiment_score   = 50.0
        fundamental_score = 50.0

        composite = (
            technical_score   * w["technical"]   +
            momentum_score    * w["momentum"]    +
            volume_score      * w["volume"]      +
            sentiment_score   * w["sentiment"]   +
            fundamental_score * w["fundamental"]
        ) * market_mult

        composite = min(max(round(composite, 1), 0), 100)

        if composite >= 78:
            signal, conviction = "STRONG BUY", "HIGH"
        elif composite >= 65:
            signal, conviction = "BUY",         "HIGH"
        elif composite >= 55:
            signal, conviction = "WATCH",       "MEDIUM"
        elif composite >= 42:
            signal, conviction = "CAUTION",     "LOW"
        else:
            signal, conviction = "AVOID",       "LOW"

        return {
            "final_score":     composite,
            "technical_score": round(technical_score, 1),
            "momentum_score":  round(momentum_score, 1),
            "volume_score":    round(volume_score, 1),
            "signal":          signal,
            "conviction":      conviction,
        }

    def compute_targets(self, df, price, signal, atr) -> dict:
        strategy = CONFIG["STRATEGY"]
        mode     = strategy.get("MODE", "AUTO_PCT")

        if mode == "AUTO_PCT" and len(df) >= 30:
            recent   = df.tail(60).copy()
            up_pct   = ((recent["high"] - recent["open"]) / recent["open"] * 100).clip(lower=0)
            down_pct = ((recent["open"] - recent["low"])  / recent["open"] * 100).clip(lower=0)

            t1p = strategy["AUTO_T1_PERCENTILE"] / 100
            t2p = strategy["AUTO_T2_PERCENTILE"] / 100
            slp = strategy["AUTO_SL_PERCENTILE"] / 100

            if signal in ("STRONG BUY", "BUY", "WATCH"):
                t1 = round(price * (1 + float(up_pct.quantile(t1p))   / 100), 2)
                t2 = round(price * (1 + float(up_pct.quantile(t2p))   / 100), 2)
                sl = round(price * (1 - float(down_pct.quantile(slp)) / 100), 2)
                max_t2 = round(price * (1 + CONFIG["MAX_INTRADAY_TARGET_PCT"] / 100), 2)
                t2 = min(t2, max_t2)
                t1 = min(t1, t2)
            else:
                t1 = round(price * (1 - float(down_pct.quantile(t1p)) / 100), 2)
                t2 = round(price * (1 - float(down_pct.quantile(t2p)) / 100), 2)
                sl = round(price * (1 + float(up_pct.quantile(slp))   / 100), 2)
                min_t2 = round(price * (1 - CONFIG["MAX_INTRADAY_TARGET_PCT"] / 100), 2)
                t2 = max(t2, min_t2)
                t1 = max(t1, t2)

        elif mode == "ATR" and atr > 0:
            if signal in ("STRONG BUY", "BUY", "WATCH"):
                t1 = round(price + CONFIG["ATR_T1_MULT"] * atr, 2)
                t2 = round(price + CONFIG["ATR_T2_MULT"] * atr, 2)
                sl = round(price - CONFIG["ATR_SL_MULT"] * atr, 2)
            else:
                t1 = round(price - CONFIG["ATR_T1_MULT"] * atr, 2)
                t2 = round(price - CONFIG["ATR_T2_MULT"] * atr, 2)
                sl = round(price + CONFIG["ATR_SL_MULT"] * atr, 2)
        else:
            t1p = strategy["TARGET_T1_PCT"] / 100
            t2p = strategy["TARGET_T2_PCT"] / 100
            slp = strategy["STOP_LOSS_PCT"]  / 100
            if signal in ("STRONG BUY", "BUY", "WATCH"):
                t1 = round(price * (1 + t1p), 2)
                t2 = round(price * (1 + t2p), 2)
                sl = round(price * (1 - slp), 2)
            else:
                t1 = round(price * (1 - t1p), 2)
                t2 = round(price * (1 - t2p), 2)
                sl = round(price * (1 + slp), 2)

        return {"t1": t1, "t2": t2, "stop_loss": sl}


# ─── Main Bot ─────────────────────────────────────────────────────────────
class PSXTradingBot:
    def __init__(self):
        self.fetcher = PSXDataFetcher()
        self.ta      = TechnicalAnalyzer()
        self.mkt     = MarketContextAnalyzer()
        self.scorer  = MasterScorer()
        self._regime = None

    def analyze_stock(self, ticker: str):
        df = self.fetcher.fetch(ticker)
        if df is None:
            return None
        ta_result = self.ta.compute_all(df)
        if ta_result is None:
            return None
        if self._regime is None:
            self._regime = self.mkt.get_regime()

        score_result = self.scorer.score(
            ta_result["technical_score"],
            ta_result["vol_ratio"],
            self._regime["multiplier"],
        )
        targets = self.scorer.compute_targets(
            ta_result["df"],
            ta_result["price"],
            score_result["signal"],
            ta_result["atr"],
        )
        return {
            "ticker":          ticker,
            "name":            STOCK_NAMES.get(ticker, ticker.replace(".KA", "")),
            "price":           ta_result["price"],
            "signal":          score_result["signal"],
            "conviction":      score_result["conviction"],
            "final_score":     score_result["final_score"],
            "technical_score": score_result["technical_score"],
            "t1":              targets["t1"],
            "t2":              targets["t2"],
            "stop_loss":       targets["stop_loss"],
            "rsi":             ta_result["rsi"],
            "macd_hist":       ta_result["macd_hist"],
            "adx":             ta_result["adx"],
            "atr":             ta_result["atr"],
            "vol_ratio":       ta_result["vol_ratio"],
            "stoch_k":         ta_result["stoch_k"],
            "mfi":             ta_result["mfi"],
            "bb_width":        ta_result["bb_width"],
            "sma20":           ta_result["sma20"],
            "sma50":           ta_result["sma50"],
            "signals":         ta_result["signals"],
            "market_regime":   self._regime["regime"],
            "df":              ta_result["df"],
        }

    def run_daily_scan(self, tickers=None):
        tickers = tickers or CONFIG["STOCK_UNIVERSE"]
        self._regime = self.mkt.get_regime()
        results = []
        for t in tickers:
            r = self.analyze_stock(t)
            if r:
                results.append(r)
        order = {"STRONG BUY": 5, "BUY": 4, "WATCH": 3, "CAUTION": 2, "AVOID": 1}
        results.sort(key=lambda x: (order.get(x["signal"], 0), x["final_score"]), reverse=True)
        return results

    def get_top_picks(self, results, n=5):
        return [r for r in results if r["signal"] in ("STRONG BUY", "BUY")][:n]


# ─── Utilities ────────────────────────────────────────────────────────────
def market_is_open() -> bool:
    now = datetime.now(PST)
    if now.weekday() >= 5:
        return False
    o = now.replace(hour=9,  minute=30, second=0, microsecond=0)
    c = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return o <= now <= c

def last_scan_time() -> str:
    return datetime.now(PST).strftime("%d %b %Y, %I:%M %p PKT")


# ─── Module-level helpers (used by app.py) ────────────────────────────────
PSX_UNIVERSE = CONFIG["STOCK_UNIVERSE"]

_bot_instance = None

def run_daily_scan(tickers=None):
    global _bot_instance
    _bot_instance = PSXTradingBot()
    return _bot_instance.run_daily_scan(tickers)

def get_top_picks(results, n=5):
    return [r for r in results if r["signal"] in ("STRONG BUY", "BUY")][:n]

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, float('nan'))
    return 100 - (100 / (1 + rs))

def compute_macd(series):
    import pandas as pd
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist   = macd - signal
    return macd, signal, hist

def compute_bollinger(series, period=20):
    sma   = series.rolling(period).mean()
    std   = series.rolling(period).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    return upper, sma, lower
