import os
from mcp.server.fastmcp import FastMCP
import ephem
import math
from datetime import datetime

MCP_PORT = int(os.getenv("MCP_PORT", "8081"))
mcp = FastMCP("celestial-mcp", host="0.0.0.0", port=MCP_PORT)

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_sign(longitude_deg: float) -> str:
    return ZODIAC_SIGNS[int(longitude_deg / 30)]

@mcp.tool()
def get_planet_positions(
    birth_date: str,    # "YYYY/MM/DD"
    birth_time: str,    # "HH:MM"
    latitude: float,
    longitude: float
) -> dict:
    """Returns the zodiac sign of each planet at the given birth date/time/location."""
    observer = ephem.Observer()
    observer.date = f"{birth_date} {birth_time}"
    observer.lat = str(latitude)
    observer.lon = str(longitude)

    planets = {
        "Sun": ephem.Sun(observer),
        "Moon": ephem.Moon(observer),
        "Mercury": ephem.Mercury(observer),
        "Venus": ephem.Venus(observer),
        "Mars": ephem.Mars(observer),
        "Jupiter": ephem.Jupiter(observer),
        "Saturn": ephem.Saturn(observer),
    }

    results = {}
    for name, body in planets.items():
        ecl = ephem.Ecliptic(body, epoch=observer.date)
        lon_deg = math.degrees(ecl.lon)
        results[name] = {
            "sign": get_sign(lon_deg),
            "degree": round(lon_deg % 30, 2)
        }
    return results

@mcp.tool()
def get_moon_phase(birth_date: str, birth_time: str) -> dict:
    """Returns the moon phase (new, waxing, full, waning) at birth."""
    obs = ephem.Observer()
    obs.date = f"{birth_date} {birth_time}"
    moon = ephem.Moon(obs)
    phase = moon.phase  # 0-100, percent illuminated
    if phase < 10:
        label = "New Moon"
    elif phase < 45:
        label = "Waxing Crescent"
    elif phase < 55:
        label = "Full Moon" if moon.phase > 50 else "First Quarter"
    elif phase < 90:
        label = "Waxing Gibbous"
    else:
        label = "Full Moon"
    return {"phase_percent": round(phase, 1), "label": label}

@mcp.tool()
def get_rising_sign(
    birth_date: str,
    birth_time: str,
    latitude: float,
    longitude: float
) -> dict:
    """Calculates the ascendant (rising sign) based on birth time and location."""
    obs = ephem.Observer()
    obs.date = f"{birth_date} {birth_time}"
    obs.lat = str(latitude)
    obs.lon = str(longitude)
    sidereal_time = float(obs.sidereal_time())
    # Simplified ascendant calculation
    asc_deg = (math.degrees(sidereal_time) + longitude) % 360
    return {"rising_sign": get_sign(asc_deg), "degree": round(asc_deg % 30, 2)}

@mcp.tool()
def get_rahu_ketu(
    birth_date: str,    # "YYYY/MM/DD"
    birth_time: str,    # "HH:MM"
    latitude: float,
    longitude: float
) -> dict:
    """
    Calculates Rahu (North Node) and Ketu (South Node) positions
    at the given birth date, time, and location.
    Rahu and Ketu are always exactly 180 degrees apart.
    """
    observer = ephem.Observer()
    observer.date = f"{birth_date} {birth_time}"
    observer.lat = str(latitude)
    observer.lon = str(longitude)

    # ephem tracks the Moon's ascending node directly
    moon = ephem.Moon(observer)

    # Get the true ascending node (Rahu)
    # ephem stores it as moon._nutation_lon — we use a more reliable method
    # by computing the Moon's node from its orbital elements
    
    # Use ephem's built-in node calculation
    rahu_ecl = ephem.degrees(moon.a_ra)   

    # More reliable: compute via Moon's orbital elements directly
    # ephem gives us the longitude of ascending node
    m = ephem.Moon()
    m.compute(observer)
    
    # Get ecliptic longitude of the Moon's ascending node
    # This is the standard way in ephem
    ecl = ephem.Ecliptic(m, epoch=observer.date)
    moon_lon = math.degrees(ecl.lon) % 360

    # The ascending node (Rahu) can be derived from ephem's
    # Moon orbital data — ephem stores _node as the longitude
    # of ascending node in radians
    rahu_lon = math.degrees(m._node) % 360
    ketu_lon = (rahu_lon + 180) % 360

    rahu_sign = get_sign(rahu_lon)
    ketu_sign = get_sign(ketu_lon)

    return {
        "Rahu": {
            "sign": rahu_sign,
            "degree": round(rahu_lon % 30, 2),
            "description": "North Node — karmic direction, what your soul is moving toward"
        },
        "Ketu": {
            "sign": ketu_sign,
            "degree": round(ketu_lon % 30, 2),
            "description": "South Node — karmic past, innate gifts carried from previous life"
        },
        "note": "Rahu and Ketu are always exactly 180 degrees apart"
    }

if __name__ == "__main__":
    mcp.run(transport="sse")