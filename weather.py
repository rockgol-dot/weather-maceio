import requests
from datetime import datetime

LAT = -9.6658
LON = -35.7350
NTFY_TOPIC = "daily_weather_mcz"

def get_condition(code):
    codes = {
        0: "Sol forte, ceu limpo",
        1: "Ceu predominantemente limpo",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Nevoa",
        51: "Garoa leve",
        53: "Garoa moderada",
        55: "Garoa intensa",
        61: "Chuva leve",
        63: "Chuva moderada",
        65: "Chuva intensa",
        80: "Pancadas de chuva leves",
        81: "Pancadas de chuva moderadas",
        82: "Pancadas de chuva intensas",
        95: "Trovoadas",
        96: "Trovoadas com granizo leve",
        99: "Trovoadas com granizo intenso",
    }
    return codes.get(code, f"Condicao {code}")

def wind_dir(degrees):
    dirs = ["N", "NE", "L", "SE", "S", "SO", "O", "NO"]
    return dirs[round(degrees / 45) % 8]

def main():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&daily=weathercode,temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,precipitation_probability_max,"
        "windspeed_10m_max,winddirection_10m_dominant,sunrise,sunset"
        "&timezone=America%2FSao_Paulo"
        "&forecast_days=2"
    )
    data = requests.get(url, timeout=15).json()
    d = data["daily"]
    i = 1
    date_obj = datetime.strptime(d["time"][i], "%Y-%m-%d")
    weekdays = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
    date_fmt = date_obj.strftime("%d/%m/%Y")
    weekday = weekdays[date_obj.weekday()]
    condition  = get_condition(d["weathercode"][i])
    temp_max   = d["temperature_2m_max"][i]
    temp_min   = d["temperature_2m_min"][i]
    precip     = d["precipitation_sum"][i]
    precip_pct = d["precipitation_probability_max"][i]
    wind_speed = d["windspeed_10m_max"][i]
    wdir       = wind_dir(d["winddirection_10m_dominant"][i])
    sunrise    = d["sunrise"][i].split("T")[1]
    sunset     = d["sunset"][i].split("T")[1]
    rain_line = (
        f"Chuva: {precip:.1f}mm ({precip_pct}% de probabilidade)"
        if precip_pct > 20
        else "Sem chuva prevista"
    )
    msg = (
        f"Previsao Maceio/AL - {weekday} ({date_fmt})\n\n"
        f"{condition}\n\n"
        f"Temp: {temp_min:.0f}C - {temp_max:.0f}C\n"
        f"{rain_line}\n"
        f"Vento: {wdir} {wind_speed:.0f} km/h\n\n"
        f"Nascer do sol: {sunrise} | Por do sol: {sunset}\n\n"
        f"Fonte: Open-Meteo"
    )
    r = requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=msg.encode("utf-8"),
        headers={
            "Title": f"Previsao Maceio/AL - {date_fmt}",
            "Priority": "high",
            "Tags": "sunny,umbrella",
            "Content-Type": "text/plain; charset=utf-8",
        },
        timeout=15,
    )
    r.raise_for_status()
    print(f"Enviado! Status: {r.status_code}")
    print(msg)

if __name__ == "__main__":
    main()
