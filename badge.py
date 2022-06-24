import badger2040
import qrcode
import json
import os

badger2040.system_speed(0) # lets save some battery

display = badger2040.Badger2040()

display.update_speed(2)

def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    # TODO: Logic for centering QR code inside box based on actual size
    size, module_size = measure_qr_code(size, code)
    display.pen(15)
    display.rectangle(ox, oy, size, size)
    display.pen(0)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)


# Name Badge Mode
def mode1(config, state, qr):
    display.pen(15)
    display.clear()
    # Hello top banner
    display.pen(0)
    display.rectangle(0, 0, 298, 40)
    display.thickness(4)
    display.font("sans")
    display.pen(15)
    display.text(config["display_name"] + "!", 86, 18, scale=1.2)
    
    # Text
    display.thickness(2)
    display.pen(0)
    # TODO: Padding alignment
    display.text("{}: {}".format(config["counters"][0]["label"], str(state["counters"]["drinks"])), 8, 60, scale=0.8)
    display.text("{}: {}".format(config["counters"][1]["label"], str(state["counters"]["twinks"])),8, 85, scale=0.8)
    display.text("{}: {}".format(config["counters"][2]["label"], str(state["counters"]["boops"])),8, 110, scale=0.8)
    
    if qr:
        code = qrcode.QRCode()
        code.set_text(config["qr_link"])
        draw_qr_code(198, 40+5, 96, code)
    else:
        image = bytearray(int(96 * 96 / 8))
        open(config["profile_picture"], "r").readinto(image)
        display.image(image, 96, 96, 198, 40)


def handle_input(state):
    # Handle counters
    if display.pressed(badger2040.BUTTON_A):
        state["counters"]["drinks"] += 1
        return True

    if display.pressed(badger2040.BUTTON_B):
        state["counters"]["twinks"] += 1
        return True
        
    if display.pressed(badger2040.BUTTON_C):
        state["counters"]["boops"] += 1
        return True
    
    # Handle pagination
    page_max = 2
    if display.pressed(badger2040.BUTTON_UP):
        state["page"] += 1
        if state["page"] >= page_max:
            state["page"] = 0
        return True
    
    if display.pressed(badger2040.BUTTON_DOWN):
        state["page"] -= 1
        if state["page"] < 0:
            state["page"] = page_max - 1
        return True
        
    
    return False


def default_state():
    return {
        "page": 0,
        "counters": {
            # TODO: Split counters based on page or some index ?
            "drinks": 0,
            "twinks": 0,
            "boops": 0
        }    
    }

def load_state(config):
    try:
        with open("/state/{}.json".format(config["profile"])) as f:
            return json.load(f)
    except OSError:
        return default_state()
    
def persist_state(config, state):
    print("persisting state:")
    print(state)
    try:
        with open("/state/{}.json".format(config["profile"]), "w") as f:
            json.dump(state, f)
    except OSError:
        # If /state doesn't exist, attempt to create it and retry.
        try:
            print("creating /state folder")
            os.stat("/state")
        except OSError:
            os.mkdir("/state")
            persist_state(config, state)
        

def render(config, state):
    # TODO: Switch to different pages based on state.page
    # TODO: Support dynamically selecting different renderers based
    # on config.pages[0].renderer
    show_qr = state["page"] == 1
    mode1(config, state, show_qr)
    display.update()

def main(config):
    state = load_state(config)
    render(config, state)
    while True:
        display.halt()
        
        changed = handle_input(state)
        if not changed:
            continue
        
        persist_state(config, state)
        render(config, state)

# Actual execution begins
config = {
    "profile": "furry", # Dictates what the stored file is called
    "display_name": "Noah", # Name shown on header ??
    "profile_picture": "pfp.bin",
    "qr_link": "f.noahstride.co.uk",
    "counters": [
        {
            "key": "drinks",
            "label": "Beers"
        },
        {
            "key": "twinks",
            "label": "Boys"
        },
        {
            "key": "boops",
            "label": "Snoots"
        }
    ]
}
main(config)

