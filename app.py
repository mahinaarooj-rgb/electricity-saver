import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier

st.set_page_config(page_title="AI Smart Electricity Saver",
                   page_icon="⚡", layout="wide")
st.title("⚡ AI Smart Electricity Saver")
st.caption("Track, predict and reduce your electricity bill")

st.sidebar.header("Settings")
rate = st.sidebar.number_input("Rate per unit (Rs)", 1.0, 200.0, 50.0)
budget = st.sidebar.number_input("Monthly budget (Rs)", 0, 500000, 5000)
days = st.sidebar.slider("Days in month", 28, 31, 30)

default = pd.DataFrame({
    "Appliance": ["Fan", "Bulb", "AC", "TV", "Fridge", "Washing Machine"],
    "Watts": [75, 20, 1000, 100, 150, 500],
    "Hours": [10, 5, 4, 4, 24, 1],
})

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "🔌 Appliances", "🤖 AI Prediction", "💡 Tips"])

with tab2:
    st.subheader("Edit or add your appliances")
    df = st.data_editor(default, num_rows="dynamic",
                        use_container_width=True)
    df = df.dropna()
    df["Daily kWh"] = df["Watts"] * df["Hours"] / 1000
    df["Monthly kWh"] = df["Daily kWh"] * days
    df["Monthly Bill"] = df["Monthly kWh"] * rate
    total_units = df["Monthly kWh"].sum()
    bill = df["Monthly Bill"].sum()
    if total_units <= 0:
        st.warning("Please add at least one appliance with hours.")
        st.stop()

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Monthly units", round(total_units, 1))
    c2.metric("Monthly bill (Rs)", round(bill))
    c3.metric("Budget left (Rs)", round(budget - bill))
    c4.metric("CO2 (kg, approx)", round(total_units * 0.45))

    if budget > 0:
        st.progress(min(bill / budget, 1.0))
    if bill > budget:
        st.error("Warning! Your bill is above the budget.")
    else:
        st.success("Good! Your bill is within the budget.")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].bar(df["Appliance"], df["Monthly Bill"])
    ax[0].set_title("Monthly bill by appliance (Rs)")
    ax[0].tick_params(axis="x", rotation=45)
    ax[1].pie(df["Monthly kWh"], labels=df["Appliance"],
              autopct="%1.0f%%")
    ax[1].set_title("Share of usage")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Savings simulator")
    sel = st.selectbox("Choose appliance", df["Appliance"])
    row = df[df["Appliance"] == sel].iloc[0]
    cut = st.slider("Reduce hours per day", 0.0, 24.0, 1.0)
    cut = min(cut, float(row["Hours"]))
    saved = row["Watts"] * cut / 1000 * days * rate
    st.info(f"Monthly saving: Rs. {saved:.0f}  |  "
            f"Yearly saving: Rs. {saved * 12:.0f}")

    st.download_button("Download report (CSV)",
                       df.to_csv(index=False).encode(),
                       "report.csv", "text/csv")

with tab3:
    st.subheader("Next month prediction")
    txt = st.text_input("Past monthly units (comma separated)",
                        "120,135,150,145")
    try:
        vals = [float(x) for x in txt.split(",") if x.strip()]
        if len(vals) < 2:
            raise ValueError
        X = [[i] for i in range(1, len(vals) + 1)]
        nxt = LinearRegression().fit(X, vals).predict(
            [[len(vals) + 1]])[0]
        a, b = st.columns(2)
        a.metric("Predicted units", round(nxt))
        b.metric("Predicted bill (Rs)", round(nxt * rate))
        st.line_chart(pd.DataFrame({"Units": vals + [nxt]}))
    except ValueError:
        st.warning("Write at least 2 numbers, like: 120,135,150")

    st.subheader("Usage level (AI classifier)")
    Xc = [[50], [80], [100], [120], [150], [180], [220], [300]]
    yc = ["Low", "Low", "Normal", "Normal",
          "High", "High", "High", "Very High"]
    tree = DecisionTreeClassifier().fit(Xc, yc)
    st.metric("Your usage level",
              tree.predict([[total_units]])[0])
    st.caption("Trained on small demo data.")

with tab4:
    st.subheader("Smart tips")
    for name, cost in zip(df["Appliance"], df["Monthly Bill"]):
        share = cost / bill * 100
        if share > 40:
            st.warning(f"{name} uses {share:.0f}% of your bill. "
                       "Try to reduce its hours.")
    st.write("- Use LED bulbs.")
    st.write("- Keep AC at 24-26 C and clean its filter.")
    st.write("- Switch off devices instead of leaving them on standby.")
    st.write("- Run heavy appliances only when needed.")
