import streamlit as st
import pandas as pd
import random
from io import BytesIO

# ====== FUNZIONI DEL SIMULATORE ======

class Bot:
    def __init__(self, name, budget, strategy):
        self.name = name
        self.budget = budget
        self.strategy = strategy
        self.team = []

    def decide_bid(self, player, current_price):
        if self.strategy == "aggressivo":
            return current_price < player["expected_value"] * 1.2 and self.budget > current_price
        elif self.strategy == "parsimonioso":
            return current_price < player["expected_value"] * 0.8 and self.budget > current_price
        elif self.strategy == "valore":
            return current_price < player["expected_value"] and self.budget > current_price
        elif self.strategy == "need_based":
            return current_price < player["expected_value"] and self.budget > current_price and len(self.team) < 5
        else:  # random
            return random.choice([True, False]) and self.budget > current_price

def run_auction(players, bots, price_increment=1):
    auction_log = []
    for _, player in players.iterrows():
        current_price = player["base_price"]
        current_winner = None
        active_bidders = bots[:]
        while active_bidders:
            bidder = random.choice(active_bidders)
            if bidder.decide_bid(player, current_price):
                current_price += price_increment
                current_winner = bidder
                if current_price > bidder.budget:
                    active_bidders.remove(bidder)
            else:
                active_bidders.remove(bidder)
        if current_winner:
            current_winner.budget -= current_price
            current_winner.team.append(player["name"])
            auction_log.append([player["name"], current_winner.name, current_price, player["role"]])
        else:
            auction_log.append([player["name"], None, None, player["role"]])
    return auction_log

# ====== INTERFACCIA STREAMLIT ======

st.title("💰 Simulatore Asta Fantacalcio")

uploaded_file = st.file_uploader("📂 Carica il CSV dei giocatori", type=["csv"])

teams = st.slider("Numero squadre", 4, 12, 8)
budget = st.slider("Budget iniziale per squadra", 100, 1000, 500)
increment = st.slider("Incremento rilancio", 1, 10, 1)
seed = st.number_input("Seed casuale (0 = random)", 0, 9999, 42)

strategies_list = ["valore", "aggressivo", "parsimonioso", "need_based", "random"]

strategies = []
for i in range(teams):
    strategies.append(st.selectbox(f"Strategia squadra {i+1}", strategies_list, index=i % len(strategies_list)))

if st.button("🚀 Avvia simulazione"):
    if uploaded_file is None:
        st.error("Carica prima un file CSV dei giocatori!")
    else:
        random.seed(seed if seed != 0 else None)
        players = pd.read_csv(uploaded_file)
        bots = [Bot(f"Squadra {i+1}", budget, strategies[i]) for i in range(teams)]
        log = run_auction(players, bots, price_increment=increment)

        df_log = pd.DataFrame(log, columns=["Giocatore", "Vincitore", "Prezzo", "Ruolo"])
        st.success("✅ Asta completata!")
        st.dataframe(df_log)

        csv_buffer = BytesIO()
        df_log.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Scarica log in CSV",
            data=csv_buffer.getvalue(),
            file_name="log_asta.csv",
            mime="text/csv"
      )
