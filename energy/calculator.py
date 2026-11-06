import math

def calculate_system(payload, appliances, products):
    """Indicative sizing. Final designs must be checked by a qualified installer."""
    pf = float(payload.get("power_factor", 0.8))
    margin = float(payload.get("inverter_margin", 1.25))
    voltage = int(payload.get("system_voltage", 48))
    backup_h = float(payload.get("backup_hours", 4))
    dod = float(payload.get("depth_of_discharge", 0.80))
    battery_eff = float(payload.get("battery_efficiency", 0.90))
    sun_hours = float(payload.get("peak_sun_hours", 5))
    pv_derate = float(payload.get("pv_derate", 0.75))
    if not 0.5 <= pf <= 1: raise ValueError("Power factor must be between 0.5 and 1.")
    if voltage not in (12, 24, 48, 96): raise ValueError("System voltage must be 12, 24, 48 or 96V.")
    if backup_h <= 0 or not 0 < dod <= 1 or not 0 < battery_eff <= 1: raise ValueError("Check backup hours and battery settings.")
    if sun_hours <= 0 or not 0 < pv_derate <= 1: raise ValueError("Peak sun hours and PV derating must be positive.")
    total_w = daily_wh = 0
    breakdown = []
    for row in payload.get("appliances", []):
        appliance_id = int(row.get("appliance_id", 0))
        appliance = appliances.get(appliance_id)
        if not appliance: raise ValueError(f"Appliance {appliance_id} was not found.")
        qty = int(row.get("quantity", 0))
        hours = float(row.get("hours", 0))
        watts = float(row.get("watts", appliance.watts))
        if qty < 0 or hours < 0 or hours > 24 or watts < 0: raise ValueError("Appliance quantities, watts and hours must be valid.")
        load = qty * watts
        energy = load * hours
        total_w += load
        daily_wh += energy
        if qty:
            breakdown.append({"name": appliance.name, "quantity": qty, "watts_each": watts,
                              "total_watts": round(load), "hours": hours, "daily_wh": round(energy)})
    if total_w <= 0: raise ValueError("Add at least one appliance with a quantity greater than zero.")

    inverter_required = total_w * margin / (1000 * pf)
    inverter_options = [p for p in products if p.category == "inverter" and p.active and p.capacity_kva]
    inverter = next((p for p in sorted(inverter_options, key=lambda x:x.capacity_kva) if p.capacity_kva >= inverter_required), None)

    battery_wh = total_w * backup_h / (dod * battery_eff)
    battery_ah = battery_wh / voltage
    chemistry = str(payload.get("battery_chemistry", "Lithium")).strip().lower()
    batteries = [p for p in products if p.category == "battery" and p.active and p.voltage and p.ah and (p.chemistry or "").lower() == chemistry]
    compatible = [p for p in batteries if p.voltage <= voltage and voltage % p.voltage == 0]
    battery = max(compatible, key=lambda p:p.ah) if compatible else None
    battery_count = series = parallel = None
    if battery:
        series = voltage // battery.voltage
        parallel = math.ceil(battery_ah / battery.ah)
        battery_count = series * parallel

    pv_required_w = daily_wh / (sun_hours * pv_derate)
    panels = [p for p in products if p.category == "panel" and p.active and p.wattage]
    panel = max(panels, key=lambda p:p.wattage) if panels else None
    panel_count = math.ceil(pv_required_w / panel.wattage) if panel else None

    lines = []
    def add_line(product, qty, label=None):
        if product and qty:
            lines.append({"product_id":product.id, "name":label or product.name, "category":product.category,
                          "quantity":qty, "unit":product.unit, "unit_price":float(product.price),
                          "line_total":round(float(product.price) * qty, 2)})
    add_line(inverter, 1)
    add_line(battery, battery_count)
    add_line(panel, panel_count)
    # Accessories and installation are configurable catalogue items. Quantities are admin defaults.
    for p in products:
        if p.active and p.category in ("accessory", "service") and p.default_qty > 0:
            add_line(p, p.default_qty)
    priced_total = round(sum(x["line_total"] for x in lines), 2)
    return {
        "total_watts":round(total_w), "daily_wh":round(daily_wh), "daily_kwh":round(daily_wh/1000,2),
        "load_kva":round(total_w/(1000*pf),2), "required_inverter_kva":round(inverter_required,2),
        "inverter":({"name":inverter.name,"capacity_kva":inverter.capacity_kva,"price":float(inverter.price)} if inverter else None),
        "system_voltage":voltage, "backup_hours":backup_h, "battery_required_wh":round(battery_wh),
        "battery_required_ah":round(battery_ah,1),
        "battery":({"name":battery.name,"spec":f"{battery.voltage}V {battery.ah}Ah","quantity":battery_count,
                    "series":series,"parallel":parallel,"unit_price":float(battery.price)} if battery else None),
        "pv_required_w":round(pv_required_w), "peak_sun_hours":sun_hours,
        "solar_panel":({"name":panel.name,"wattage":panel.wattage,"quantity":panel_count,"unit_price":float(panel.price)} if panel else None),
        "breakdown":breakdown, "items":lines, "estimated_total":priced_total,
        "warnings":[
          "Sizing is indicative, not a certified electrical design.",
          "The battery estimate assumes the full connected load runs simultaneously for the entire backup period.",
          "Starting surge, motor loads, inverter efficiency, cable losses, temperature, battery discharge limits and manufacturer requirements must be checked.",
          "PV sizing uses daily energy, peak-sun-hours and a system derating factor. Actual solar yield varies by location, season, shading and panel orientation.",
          "Accessory and service quantities are catalogue defaults set by the administrator. Confirm cable lengths, protection ratings, mounting and installation scope on site."
        ]
    }
