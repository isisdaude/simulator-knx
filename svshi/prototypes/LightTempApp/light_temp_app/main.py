from instances import app_state, svshi_api, LED, BUTTON, THERMOMETER

def invariant() -> bool:
    # Write the invariants of the app here
    # It can be any boolean expressions containing the read properties of the devices and constants
    # You CANNOT use external libraries here, nor unchecked functions
    return True


def iteration():
    if THERMOMETER.read() < 21:
        LED.on()
    else:
        LED.off()

    # Write your app code here
    # You CANNOT use external libraries here, encapsulate calls to those in functions whose names start
    # with "unchecked" and use these functions instead
    pass
