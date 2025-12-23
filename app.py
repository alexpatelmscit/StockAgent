import sys
from agent import StockAgent

def get_user_inputs():
    try:
        base_amount = input("Enter investment amount (₹) or press Enter for default (10000): ")
        sectors = input("Enter sectors separated by commas (e.g., metals, pharma) or press Enter for auto-pick (Top 10 Buys): ")
        print("Choose investment frequency:")
        print("1. Monthly")
        print("2. Quarterly")
        print("3. Half-Yearly")
        print("4. Yearly")
        choice = input("Enter choice (1-4) or press Enter for default (Monthly): ")

        frequency_map = {
            "1": "monthly",
            "2": "quarterly",
            "3": "half_yearly",
            "4": "yearly"
        }

        config = {
            "base_amount": float(base_amount) if base_amount else 10000,
            "sectors": [s.strip() for s in sectors.split(",")] if sectors else [],
            "frequency": frequency_map.get(choice, "monthly")
        }
        return config
    except Exception as e:
        print("⚠️ Error in input:", e)
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "summary":
        agent = StockAgent({"base_amount": 0, "sectors": []})
        agent.summary()
    else:
        config = get_user_inputs()10
        agent = StockAgent(config)
        agent.run()
