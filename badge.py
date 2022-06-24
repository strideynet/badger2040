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
    display.rectangle(0, 0, 298, 40)
    display.thickness(4)
    display.font("sans")
    display.pen(15)
    display.text(config["display_name"] + "!", 86, 18, scale=1.2)
    
    # Text
    display.thickness(2)
    display.pen(0)

    # TODO: Padding alignment
    counter_y = 60
    for counter in config["counters"]:
        display.text("{}: {}".format(counter["label"], str(state["counters"][counter["key"]])), 8, counter_y, scale=0.8)
        counter_y += 25
    
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
        state["counters"][config["counters"][0]["key"]] += 1
        return True

    if display.pressed(badger2040.BUTTON_B):
        state["counters"][config["counters"][1]["key"]] += 1
        return True
        
    if display.pressed(badger2040.BUTTON_C):
        state["counters"][config["counters"][2]["key"]] += 1
        return True
    
    # Handle pagination
    page_max = 3
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

def load_state(config):
    state = {}
    try:
        with open("/state/{}.json".format(config["profile"])) as f:
            state = json.load(f)
    except OSError:
        # Default state
        state = {
            "page": 0,
            "counters": {}    
        }
    
    # Add zeroed out values for new counters
    for counter in config["counters"]:
        if counter["key"] not in state["counters"]:
            state["counters"][counter["key"]] = 0

    return state
    
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

    # Start from a fresh slate, with display cleared, and pen reset to black.
    display.pen(15)
    display.clear()
    display.pen(0)

    page = state["page"]
    if page == 0:
        mode1(config, state, False)
    elif page == 1:
        mode1(config, state, True)
    elif page == 2:
        display.thickness(2)
        display.font("sans")
        display.text("Mystery third page", 0, 50, scale=1)
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
            "label": "Drinks"
        },
        {
            "key": "twinks",
            "label": "Boys"
        },
        {
            "key": "boops",
            "label": "Boops"
        }
    ]
}
main(config)

