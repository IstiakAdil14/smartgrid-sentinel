def generate_explanation(risk: str, evidence: dict) -> str:
    """
    Rule-based natural-language explanation layer.
    Generates a human-readable explanation based on actual SmartGrid telemetry
    without claiming strict causality.
    """
    load = evidence.get('transformer_load', 0)
    demand = evidence.get('electricity_demand', 0)
    renewable = evidence.get('renewable_generation', 0)
    temperature = evidence.get('temperature', 0)
    rainfall = evidence.get('rainfall', 0)

    sentences = []

    if risk == "High":
        sentences.append("The grid is showing signs of significant stress.")
    elif risk == "Medium":
        sentences.append("The grid is currently under moderate stress.")
    else:
        sentences.append("The grid is currently operating under stable conditions.")

    if load >= 80:
        sentences.append(
            f"The transformer is heavily loaded at {load:.1f}%, "
            "so continued monitoring is important."
        )
    elif load >= 60:
        sentences.append(
            f"The transformer is operating at {load:.1f}% load, "
            "which indicates moderate loading."
        )
    else:
        sentences.append(
            f"The transformer is operating at {load:.1f}% load, "
            "which is currently within a comfortable range."
        )

    if renewable < demand * 0.2:
        sentences.append(
            f"Renewable generation is relatively low at {renewable:.1f} MW "
            f"compared with demand of {demand:.1f} MW."
        )
    else:
        sentences.append(
            f"Electricity demand is {demand:.1f} MW, with renewable generation contributing {renewable:.1f} MW."
        )

    if rainfall > 10:
        sentences.append("Heavy rainfall may add additional operational stress.")
    elif rainfall == 0:
        sentences.append("There is currently no rainfall, so weather conditions are not adding significant stress.")
    else:
        sentences.append(f"There is currently {rainfall:.1f} mm of rainfall.")

    return " ".join(sentences)


def generate_recommendations(risk: str, evidence: dict) -> list:
    """
    Generates user-oriented suggestions based on grid risk.
    """
    if risk == "Low":
        return [
            "✓ Normal electricity usage can continue.",
            "✓ No special precautions are needed.",
            "✓ Continue using electrical appliances as usual."
        ]
    elif risk == "Medium":
        return [
            "• Avoid unnecessary high-power appliance usage during peak hours.",
            "• Charge essential devices such as phones and laptops.",
            "• Keep emergency lighting available as a precaution.",
            "• Stay informed about local power updates."
        ]
    else:
        return [
            "⚠ Charge essential devices immediately.",
            "⚠ Limit non-essential electricity consumption.",
            "⚠ Keep backup lighting or power sources ready.",
            "⚠ Save important work and data.",
            "⚠ Follow announcements from the local electricity authority."
        ]
