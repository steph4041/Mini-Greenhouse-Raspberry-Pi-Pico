from machine import Pin, ADC
import utime, network, socket

segments = [Pin(i, Pin.OUT, Pin.PULL_DOWN) for i in [2,0,6,4,3,1,7,5]]
digits = [Pin(i, Pin.OUT, Pin.PULL_DOWN) for i in [9,8,10]]

NUMBERS = [
    [1,1,1,1,1,1,0,0], [0,1,1,0,0,0,0,0], [1,1,0,1,1,0,1,0],
    [1,1,1,0,1,0,1,0], [0,1,1,0,0,1,1,0], [1,0,1,0,1,1,1,0],
    [1,0,1,1,1,1,1,0], [1,1,1,0,0,0,0,0], [1,1,1,1,1,1,1,0],
    [1,1,1,0,1,1,1,0]
]
LETTERS = {
    'E':[1,0,0,1,1,1,1,0],'A':[1,1,1,1,0,1,1,0],'N':[0,0,1,1,0,0,1,0],
    'L':[0,0,0,1,1,1,0,0],'D':[0,1,1,1,1,0,1,0],'F':[1,0,0,1,0,1,1,0],
    'U':[0,1,1,1,1,1,0,0],'P':[1,1,0,1,0,1,1,0],'M':[1,1,1,1,0,1,0,0]
}

pot_temp = ADC(26)
adc_soil = ADC(28)
ldr = ADC(27)
sens_acqua = Pin(18, Pin.IN, Pin.PULL_UP)

fan = Pin(19, Pin.OUT)
led = Pin(13, Pin.OUT)
pump = Pin(17, Pin.OUT)

fan.value(0)
led.value(0)
pump.value(0)

overrides = {"ventola": None, "led": None, "pompa": None}

def leggi_soglie():
    temp_max = 25
    soil_min = 60
    return {"temp_max": temp_max, "temp_min": 18.0, "umid_suolo_min": soil_min}

def display_number(num):
    num_str = str(num)
    num_len = len(num_str)

    if num_len == 1:
        digits_val = [0, 0, int(num_str[0])]
    elif num_len == 2:
        digits_val = [0, int(num_str[0]), int(num_str[1])]
    else:
        digits_val = [int(num_str[0]), int(num_str[1]), int(num_str[2])]

    delay = 0.001

    for i in range(3):
        for d in digits:
            d.value(0)
        for seg, val in zip(segments, NUMBERS[digits_val[i]]):
            seg.value(val)
        digits[i].value(1)
        utime.sleep(delay)
        digits[i].value(0)

def display_error(code):
    E_PATTERN = LETTERS['E']
    c_str = "{:02d}".format(code)
    patterns = [
        E_PATTERN,
        NUMBERS[int(c_str[0])],
        NUMBERS[int(c_str[1])]
    ]

    t_start = utime.ticks_ms()
    while utime.ticks_diff(utime.ticks_ms(), t_start) < 1000:
        for i in range(3):
            for d in digits:
                d.value(0)
            for seg, val in zip(segments, patterns[i]):
                seg.value(val)
            digits[i].value(1)
            utime.sleep_ms(5)
            digits[i].value(0)
    for d in digits:
        d.value(0)

def leggi_sensori():
    temp = pot_temp.read_u16() * 100 / 65535
    soil = adc_soil.read_u16() * 100 / 65535
    acqua = sens_acqua.value() == 1
    luce = ldr.read_u16() * 100 / 65535
    print(f"temp={temp:.1f}, soil={soil:.1f}, luce={luce:.1f}, acqua={'OK' if acqua else 'ASSENTE'}")
    return {"temp": temp, "soil": soil, "acqua": acqua, "luce": luce}

def controlla(s, soglie):
    if not s['acqua']:
        fan.value(0); led.value(0); pump.value(0)
        display_error(4)
        return

    if overrides['ventola'] is not None:
        fan.value(overrides['ventola'])
    else:
        fan.value(1) if s['temp'] >= soglie['temp_max'] else fan.value(0)

    if overrides['led'] is not None:
        led.value(overrides['led'])
    else:
        led.value(1) if s['luce'] < 70 else led.value(0)

    if overrides['pompa'] is not None:
        pump.value(overrides['pompa'])
    else:
        pump.value(1) if s['soil'] < soglie['umid_suolo_min'] else pump.value(0)

def pagina(s, o, soglie):
    stato = lambda p: "ON" if p.value() else "OFF"
    return f"""HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html>
<html><head><meta http-equiv='refresh' content='5'><style>
body {{font-family:sans-serif;background:#eef}}
div {{margin:10px;padding:10px;background:#fff;border-radius:8px}}
button {{margin:5px;padding:10px 20px;font-size:16px;border:none;border-radius:5px;cursor:pointer}}
.auto {{background-color:#ccc}}
.on {{background-color:#4CAF50;color:white}}
.off {{background-color:#f44336;color:white}}
</style></head><body>
<h1>Serra Automatica</h1>
<div>Temp: {s['temp']:.1f} °C | Suolo: {s['soil']:.1f}% | Acqua: {'OK' if s['acqua'] else 'ASSENTE'} | Luce: {s['luce']:.1f}%</div>
<div>Ventola: {stato(fan)} | LED: {stato(led)} | Pompa: {stato(pump)}</div>
<form method="GET">
    <div>
        <p><strong>Ventola</strong></p>
        <button name="fan" value="auto" class="auto">Auto</button>
        <button name="fan" value="on" class="on">ON</button>
        <button name="fan" value="off" class="off">OFF</button>
    </div>
    <div>
        <p><strong>LED</strong></p>
        <button name="led" value="auto" class="auto">Auto</button>
        <button name="led" value="on" class="on">ON</button>
        <button name="led" value="off" class="off">OFF</button>
    </div>
    <div>
        <p><strong>Pompa</strong></p>
        <button name="pump" value="auto" class="auto">Auto</button>
        <button name="pump" value="on" class="on">ON</button>
        <button name="pump" value="off" class="off">OFF</button>
    </div>
</form>
        <script>
            setInterval(() => location.reload(), 1500)
        </script>
<div>Soglie: TempMax = {soglie['temp_max']:.1f} °C | SuoloMin = {soglie['umid_suolo_min']:.1f}%</div>
</body></html>"""

ssid, password = "Vodafone-CV24GHz", "MammaLucia2006!"
sta = network.WLAN(network.STA_IF);
sta.active(True)
sta.connect(ssid, password)
t0 = utime.ticks_ms()
while not sta.isconnected() and utime.ticks_diff(utime.ticks_ms(), t0) < 10000:
    utime.sleep_ms(200)
if sta.isconnected():
    ip = sta.ifconfig()[0]
    print(f"[WIFI] Connesso a WiFi, IP: {ip}")
else:
    print("[WIFI] Connessione fallita entro 10s")
    raise RuntimeError("E04: impossibile connettersi al WiFi")

s = socket.socket(); s.bind(('',80)); s.listen(1); s.setblocking(True)

while True:
    temp = pot_temp.read_u16() * 100 / 65535
    tempint = int(temp)
    for _ in range(100): 
        display_number(tempint)

    soglie = leggi_soglie()
    try:
        s_data = leggi_sensori()
        controlla(s_data, soglie)
    except Exception:
        display_error(07)
        print("errore sensori")
        continue
    try:
        cl, addr = s.accept()
        req = cl.recv(1024).decode()

        if 'fan=on' in req: overrides['ventola'] = True
        elif 'fan=off' in req: overrides['ventola'] = False
        elif 'fan=auto' in req: overrides['ventola'] = None

        if 'led=on' in req: overrides['led'] = True
        elif 'led=off' in req: overrides['led'] = False
        elif 'led=auto' in req: overrides['led'] = None

        if 'pump=on' in req: overrides['pompa'] = True
        elif 'pump=off' in req: overrides['pompa'] = False
        elif 'pump=auto' in req: overrides['pompa'] = None

        cl.send(pagina(s_data, overrides, soglie))
        cl.close()

    except OSError:
        pass
    utime.sleep_ms(10)
