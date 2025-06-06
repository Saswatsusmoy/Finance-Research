import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
import ta
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend import IchimokuIndicator, PSARIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
import scipy.signal as signal

def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20, window_dev: int = 2) -> pd.DataFrame:
    """Calculate Bollinger Bands"""
    indicator_bb = BollingerBands(close=df["Close"], window=window, window_dev=window_dev)
    df['bb_high'] = indicator_bb.bollinger_hband()
    df['bb_mid'] = indicator_bb.bollinger_mavg()
    df['bb_low'] = indicator_bb.bollinger_lband()
    df['bb_width'] = indicator_bb.bollinger_wband()
    df['bb_pct_b'] = indicator_bb.bollinger_pband()
    return df

def calculate_ichimoku_cloud(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Ichimoku Cloud indicator"""
    indicator_ichi = IchimokuIndicator(high=df["High"], low=df["Low"])
    df['ichimoku_a'] = indicator_ichi.ichimoku_a()  # Senkou Span A
    df['ichimoku_b'] = indicator_ichi.ichimoku_b()  # Senkou Span B
    df['ichimoku_conversion_line'] = indicator_ichi.ichimoku_conversion_line()  # Tenkan-sen
    df['ichimoku_base_line'] = indicator_ichi.ichimoku_base_line()  # Kijun-sen
    df['ichimoku_lagging_line'] = df['Close'].shift(-26)  # Chikou Span
    return df

def calculate_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Calculate Average True Range for volatility"""
    indicator_atr = AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=window)
    df['atr'] = indicator_atr.average_true_range()
    return df

def calculate_stochastic(df: pd.DataFrame, window: int = 14, smooth_window: int = 3) -> pd.DataFrame:
    """Calculate Stochastic Oscillator"""
    indicator_stoch = StochasticOscillator(high=df["High"], low=df["Low"], close=df["Close"], 
                                          window=window, smooth_window=smooth_window)
    df['stoch_k'] = indicator_stoch.stoch()  # Fast %K
    df['stoch_d'] = indicator_stoch.stoch_signal()  # Slow %D
    return df

def calculate_parabolic_sar(df: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.DataFrame:
    """Calculate Parabolic SAR indicator"""
    indicator_psar = PSARIndicator(high=df["High"], low=df["Low"], close=df["Close"], 
                                 step=step, max_step=max_step)
    df['psar'] = indicator_psar.psar()
    df['psar_up'] = indicator_psar.psar_up()
    df['psar_down'] = indicator_psar.psar_down()
    df['psar_up_indicator'] = indicator_psar.psar_up_indicator()
    df['psar_down_indicator'] = indicator_psar.psar_down_indicator()
    return df

def calculate_fibonacci_levels(df: pd.DataFrame, period: int = 120) -> Dict[str, float]:
    """Calculate Fibonacci retracement levels based on recent high/low"""
    recent_df = df.tail(period)
    max_price = recent_df["High"].max()
    min_price = recent_df["Low"].min()
    diff = max_price - min_price
    
    # Fibonacci retracement levels: 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%
    levels = {
        "0%": min_price,
        "23.6%": min_price + 0.236 * diff,
        "38.2%": min_price + 0.382 * diff,
        "50%": min_price + 0.5 * diff,
        "61.8%": min_price + 0.618 * diff,
        "78.6%": min_price + 0.786 * diff,
        "100%": max_price
    }
    
    return levels

def detect_head_and_shoulders(df: pd.DataFrame, window: int = 20) -> Dict[str, Union[bool, Dict[str, int]]]:
    """
    Detect head and shoulders pattern
    Returns a dictionary with pattern detection results
    """
    # Use peak detection to find potential head and shoulders
    # We'll use scipy's find_peaks function
    try:
        # Smooth the data to reduce noise
        smooth_close = df['Close'].rolling(window=5).mean().dropna().values
        
        # Find peaks (potential shoulders and head)
        peaks, _ = signal.find_peaks(smooth_close, distance=window)
        
        if len(peaks) < 3:
            return {"detected": False}
        
        # Find troughs (neckline points)
        troughs, _ = signal.find_peaks(-smooth_close, distance=window)
        
        if len(troughs) < 2:
            return {"detected": False}
        
        # Check for head and shoulders pattern
        # Basic check: we need at least 3 peaks and 2 troughs in the right order
        # Peak - Trough - Higher Peak - Trough - Peak
        for i in range(len(peaks) - 2):
            # Check for three consecutive peaks
            p1, p2, p3 = peaks[i], peaks[i+1], peaks[i+2]
            
            # Check if the middle peak (head) is higher than the two surrounding peaks (shoulders)
            if smooth_close[p2] > smooth_close[p1] and smooth_close[p2] > smooth_close[p3]:
                # Find troughs between peaks
                t1 = next((t for t in troughs if p1 < t < p2), None)
                t2 = next((t for t in troughs if p2 < t < p3), None)
                
                if t1 is not None and t2 is not None:
                    # Check if the troughs are at similar levels (neckline)
                    if abs(smooth_close[t1] - smooth_close[t2]) < 0.03 * smooth_close[t1]:
                        return {
                            "detected": True,
                            "pattern_type": "head_and_shoulders",
                            "positions": {
                                "left_shoulder": p1,
                                "head": p2,
                                "right_shoulder": p3,
                                "left_trough": t1,
                                "right_trough": t2
                            },
                            "neckline_value": (smooth_close[t1] + smooth_close[t2]) / 2
                        }
        
        # Check for inverse head and shoulders pattern
        for i in range(len(troughs) - 2):
            # Check for three consecutive troughs
            t1, t2, t3 = troughs[i], troughs[i+1], troughs[i+2]
            
            # Check if the middle trough (head) is lower than the two surrounding troughs (shoulders)
            if smooth_close[t2] < smooth_close[t1] and smooth_close[t2] < smooth_close[t3]:
                # Find peaks between troughs
                p1 = next((p for p in peaks if t1 < p < t2), None)
                p2 = next((p for p in peaks if t2 < p < t3), None)
                
                if p1 is not None and p2 is not None:
                    # Check if the peaks are at similar levels (neckline)
                    if abs(smooth_close[p1] - smooth_close[p2]) < 0.03 * smooth_close[p1]:
                        return {
                            "detected": True,
                            "pattern_type": "inverse_head_and_shoulders",
                            "positions": {
                                "left_shoulder": t1,
                                "head": t2,
                                "right_shoulder": t3,
                                "left_peak": p1,
                                "right_peak": p2
                            },
                            "neckline_value": (smooth_close[p1] + smooth_close[p2]) / 2
                        }
        
        return {"detected": False}
    except Exception as e:
        return {"detected": False, "error": str(e)}

def detect_double_top_bottom(df: pd.DataFrame, window: int = 20, threshold: float = 0.03) -> Dict[str, Union[bool, str, Dict]]:
    """
    Detect double top or double bottom patterns
    Returns a dictionary with pattern detection results
    """
    try:
        # Smooth the data to reduce noise
        smooth_close = df['Close'].rolling(window=5).mean().dropna().values
        
        # Find peaks and troughs
        peaks, _ = signal.find_peaks(smooth_close, distance=window)
        troughs, _ = signal.find_peaks(-smooth_close, distance=window)
        
        # Check for double top
        if len(peaks) >= 2:
            for i in range(len(peaks) - 1):
                # Check if two peaks are at similar levels
                if abs(smooth_close[peaks[i]] - smooth_close[peaks[i+1]]) < threshold * smooth_close[peaks[i]]:
                    # Check if there's a trough between them
                    middle_troughs = [t for t in troughs if peaks[i] < t < peaks[i+1]]
                    if middle_troughs:
                        return {
                            "detected": True,
                            "pattern_type": "double_top",
                            "positions": {
                                "first_peak": peaks[i],
                                "second_peak": peaks[i+1],
                                "middle_trough": middle_troughs[0]
                            },
                            "pattern_value": (smooth_close[peaks[i]] + smooth_close[peaks[i+1]]) / 2
                        }
        
        # Check for double bottom
        if len(troughs) >= 2:
            for i in range(len(troughs) - 1):
                # Check if two troughs are at similar levels
                if abs(smooth_close[troughs[i]] - smooth_close[troughs[i+1]]) < threshold * smooth_close[troughs[i]]:
                    # Check if there's a peak between them
                    middle_peaks = [p for p in peaks if troughs[i] < p < troughs[i+1]]
                    if middle_peaks:
                        return {
                            "detected": True,
                            "pattern_type": "double_bottom",
                            "positions": {
                                "first_trough": troughs[i],
                                "second_trough": troughs[i+1],
                                "middle_peak": middle_peaks[0]
                            },
                            "pattern_value": (smooth_close[troughs[i]] + smooth_close[troughs[i+1]]) / 2
                        }
        
        return {"detected": False}
    except Exception as e:
        return {"detected": False, "error": str(e)}

def detect_cup_and_handle(df: pd.DataFrame, window: int = 20) -> Dict[str, Union[bool, Dict]]:
    """
    Detect cup and handle pattern
    Returns a dictionary with pattern detection results
    """
    try:
        # We need a substantial amount of data for this pattern
        if len(df) < 60:
            return {"detected": False, "reason": "insufficient_data"}
        
        # Smooth the data to reduce noise
        smooth_close = df['Close'].rolling(window=5).mean().dropna().values
        
        # Find peaks and troughs
        peaks, _ = signal.find_peaks(smooth_close, distance=window)
        troughs, _ = signal.find_peaks(-smooth_close, distance=window)
        
        if len(peaks) < 2 or len(troughs) < 1:
            return {"detected": False, "reason": "insufficient_peaks_troughs"}
        
        # Cup and handle: peak, rounded bottom (cup), smaller peak, small dip, then breakout
        for i in range(len(peaks) - 1):
            # First peak
            p1 = peaks[i]
            
            # Look for a trough after the first peak (bottom of cup)
            cup_troughs = [t for t in troughs if t > p1]
            if not cup_troughs:
                continue
            
            cup_bottom = cup_troughs[0]
            
            # Second peak after the cup (should be near the height of first peak)
            handle_peaks = [p for p in peaks if p > cup_bottom]
            if len(handle_peaks) < 1:
                continue
                
            p2 = handle_peaks[0]
            
            # Check if second peak is close to first peak height (cup lip)
            if abs(smooth_close[p1] - smooth_close[p2]) > 0.05 * smooth_close[p1]:
                continue
                
            # Look for a small dip after the second peak (handle)
            handle_troughs = [t for t in troughs if t > p2]
            if not handle_troughs:
                continue
                
            handle_bottom = handle_troughs[0]
            
            # Handle should be shallower than the cup
            if (smooth_close[p2] - smooth_close[handle_bottom]) < 0.3 * (smooth_close[p1] - smooth_close[cup_bottom]):
                # Check for upward movement after the handle
                if handle_bottom < len(smooth_close) - 5:
                    if smooth_close[-1] > smooth_close[p2]:
                        return {
                            "detected": True,
                            "pattern_type": "cup_and_handle",
                            "positions": {
                                "cup_start": p1,
                                "cup_bottom": cup_bottom,
                                "cup_end": p2,
                                "handle_bottom": handle_bottom
                            }
                        }
        
        return {"detected": False}
    except Exception as e:
        return {"detected": False, "error": str(e)}

def detect_flag_pennant(df: pd.DataFrame, window: int = 10) -> Dict[str, Union[bool, str, Dict]]:
    """
    Detect flag or pennant patterns
    Returns a dictionary with pattern detection results
    """
    try:
        # Need a substantial trend before the flag/pennant
        if len(df) < 20:
            return {"detected": False, "reason": "insufficient_data"}
        
        # Check for a strong price move (pole)
        recent_df = df.tail(20)
        price_change = (recent_df['Close'].iloc[-1] - recent_df['Close'].iloc[0]) / recent_df['Close'].iloc[0]
        
        # Need at least 5% move for the pole
        if abs(price_change) < 0.05:
            return {"detected": False, "reason": "insufficient_trend"}
        
        # Determine if it's a bullish or bearish pattern
        is_bullish = price_change > 0
        
        # Last 5-10 bars should be consolidating (flag/pennant)
        consolidation_df = df.tail(window)
        consolidation_high = consolidation_df['High'].max()
        consolidation_low = consolidation_df['Low'].min()
        
        # Calculate the consolidation range as a percentage
        consolidation_range = (consolidation_high - consolidation_low) / consolidation_low
        
        # Flag/pennant should have a narrow range compared to the pole
        if consolidation_range < 0.5 * abs(price_change):
            # Check for converging trend lines (pennant) or parallel (flag)
            highs = consolidation_df['High'].values
            lows = consolidation_df['Low'].values
            
            # Linear regression on highs and lows
            x = np.arange(len(highs))
            high_slope, _ = np.polyfit(x, highs, 1)
            low_slope, _ = np.polyfit(x, lows, 1)
            
            # Pennant: converging trend lines
            if (is_bullish and high_slope < 0 and low_slope > 0) or (not is_bullish and high_slope > 0 and low_slope < 0):
                return {
                    "detected": True,
                    "pattern_type": "pennant",
                    "direction": "bullish" if is_bullish else "bearish"
                }
            
            # Flag: parallel trend lines
            if (abs(high_slope - low_slope) < 0.001) and ((is_bullish and high_slope < 0) or (not is_bullish and high_slope > 0)):
                return {
                    "detected": True,
                    "pattern_type": "flag",
                    "direction": "bullish" if is_bullish else "bearish"
                }
        
        return {"detected": False}
    except Exception as e:
        return {"detected": False, "error": str(e)}

def calculate_all_indicators(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Calculate all advanced indicators and detect patterns
    Returns the dataframe with indicators and a dict of pattern detection results
    """
    # Make a copy to avoid modifying the original dataframe
    df_copy = df.copy()
    
    # Calculate indicators
    df_copy = calculate_bollinger_bands(df_copy)
    df_copy = calculate_ichimoku_cloud(df_copy)
    df_copy = calculate_atr(df_copy)
    df_copy = calculate_stochastic(df_copy)
    df_copy = calculate_parabolic_sar(df_copy)
    
    # Calculate Fibonacci levels
    fib_levels = calculate_fibonacci_levels(df_copy)
    
    # Detect patterns
    patterns = {
        "head_and_shoulders": detect_head_and_shoulders(df_copy),
        "double_top_bottom": detect_double_top_bottom(df_copy),
        "cup_and_handle": detect_cup_and_handle(df_copy),
        "flag_pennant": detect_flag_pennant(df_copy)
    }
    
    # Compile results
    results = {
        "fibonacci_levels": fib_levels,
        "patterns": patterns
    }
    
    return df_copy, results 