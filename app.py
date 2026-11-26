import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.title("⚡ AI Smart Electricity Saver")

devices = {}
for name, w, h in [("Fan", 75, 10), ("Bulb", 20, 5), ("AC", 1000, 4)]:
    c1, c2 = st.columns(2)
    watts = c1.number_input(name + " Watts", 0, 5000, w)
    hours = c2.number_input(name + " Hours", 0, 24, h)
    devices[name] = (watts, hours)

rate = st.number_input("Rate per unit (Rs)", 1, 200, 50)
budget = st.number_input("Monthly budget (Rs)", 0, 200000, 5000)
reduce = st.number_input("Reduce AC hours", 0, 24, 1)
history = st.text_input("Past units", "120,135,150,145")

if st.button("Calculate"):
    units = {n: w * h / 1000 for n, (w, h) in devices.items()}
    daily = sum(units.values())
    bill = daily * 30 * rate

    st.metric("Daily Units", round(daily, 2))
    st.metric("Monthly Bill (Rs)", round(bill))

    if bill > budget:
        st.error("Warning! Your bill is above the budget.")
    else:
        st.success("Good! Your bill is within the budget.")

    w, h = devices["AC"]
    new_ac = w * max(h - reduce, 0) / 1000
    new_bill = (daily - units["AC"] + new_ac) * 30 * rate
    st.info("Monthly Savings: Rs. " + str(round(bill - new_bill)))
    st.warning("Highest usage: " + max(units, key=units.get))

    if daily > 0:
        fig, ax = plt.subplots(1, 2, figsize=(9, 3))
        ax[0].bar(units.keys(), units.values())
        ax[1].pie(units.values(), labels=units.keys(),
                  autopct="%1.1f%%")
        st.pyplot(fig)

    try:
        hist = [float(x) for x in history.split(",")]
        X = [[i] for i in range(1, len(hist) + 1)]
        nxt = LinearRegression().fit(X, hist).predict([[len(hist) + 1]])[0]
        st.metric("AI: next month units", round(nxt))
    except ValueError:
        st.warning("Write past units like: 120,135,150")
      
