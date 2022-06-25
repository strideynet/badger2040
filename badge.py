import badger2040
import qrcode
import json
import os

badger2040.system_speed(0) # lets save some battery

display = badger2040.Badger2040()

display.update_speed(2)
class CounterPage():
    def __init__(self, qr_url):
        self.qr_url = qr_url

    def measure_qr_code(self, size, code):
        w, h = code.get_size()
        module_size = int(size / w)
        return module_size * w, module_size

    def draw_qr_code(self, ox, oy, size, code):
        # TODO: Logic for centering QR code inside box based on actual size
        size, module_size = self.measure_qr_code(size, code)
        display.pen(15)
        display.rectangle(ox, oy, size, size)
        display.pen(0)
        for x in range(size):
            for y in range(size):
                if code.get_module(x, y):
                    display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)

    def render(self, config, state):
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
        
        if self.qr_url != "":
            code = qrcode.QRCode()
            code.set_text(self.qr_url)
            self.draw_qr_code(198, 40+5, 96, code)
        else:
            image = bytearray(int(96 * 96 / 8))
            open(config["profile_picture"], "r").readinto(image)
            display.image(image, 96, 96, 198, 40)

class AboutMePage():
    def __init__(self, lines):
        self.lines = lines
    def render(self, config, state):
        display.rectangle(0, 0, 298, 40)
        display.thickness(4)
        display.font("sans")
        display.pen(15)
        display.text(config["display_name"] + "!", 86, 18, scale=1.2)
        
        # Text
        display.thickness(2)
        display.pen(0)
        y = 60
        for line in self.lines:
            display.text(line, 8, y, scale=0.8)
            y += 25

        image = bytearray(int(96 * 96 / 8))
        open(config["profile_picture"], "r").readinto(image)
        display.image(image, 96, 96, 198, 40)

class StatusPage():
    def render(self, config, state):
        display.thickness(2)
        display.font("sans")
        display.text("Mystery third page", 0, 50, scale=1)

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
    page_max = len(config["pages"])
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

    # If number of configured pages has decreased, ensure current selected page
    # does not exceed threshold.
    if state["page"] >= len(config["pages"]):
        state["page"] = len(config["pages"]) - 1

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
    # Start from a fresh slate, with display cleared, and pen reset to black.
    display.pen(15)
    display.clear()
    display.pen(0)

    pageNumber = state["page"]
    page = config["pages"][pageNumber]
    page.render(config, state)
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
    ],
    "pages": [
        # Page must implement `.render(config, state)` to be valid :D
        AboutMePage(["barq.social", "Backend Engnr", "Free hugs!!"]),
        CounterPage(""),
        CounterPage("f.noahstride.co.uk"),
    ]
}
main(config)

