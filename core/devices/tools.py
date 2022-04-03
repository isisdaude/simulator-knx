
def required_power(desired_temperature=20, volume=1, insulation_state="good"):
    def temp_to_watts(temp):  # Useful watts required to heat 1m3 to temp
        dist = 18 - temp
        return 70 - (dist * 7)/2
    desired_wattage = volume*temp_to_watts(desired_temperature)
    desired_wattage += desired_wattage * \
        insulation_to_correction_factor[insulation_state]
    return desired_wattage


def max_temperature_in_room(power, volume=1, insulation_state="good"):
    """Maximum reachable temperature for this heater in the specified room"""

    def watts_to_temp(self, watts):
        return ((watts - 70)*2)/7 + 18
    watts = power / \
        ((1+insulation_to_correction_factor[insulation_state])*volume)
    return watts_to_temp(watts)


insulation_to_correction_factor = {
    "average": 0, "good": -10/100, "bad": 15/100}
"""Situation of the insulation of the room associated to the correction factor for the heating"""
