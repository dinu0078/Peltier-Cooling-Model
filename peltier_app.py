import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Peltier Model", layout="wide")
st.title("Peltier Arm Cooling Model - 3 Case Comparison")

# Fixed values
V = 12
COP = 0.35
Tskin = 35
Tcold = 25
Tamb = 40
Ttarget = 45

L = 0.24
W = 0.04
t = 0.001
rho = 1.15
Cp = 1005
mu = 1.9e-5

colors = ["blue", "green", "orange"]


# Model
def model(N, I, sg, k, H, fg, CFM):

    sg = sg/1000
    H = H/1000
    fg = fg/1000

    A = N*0.04*0.04
    P = N*V*I

    Rskin = sg/(k*A) + 0.1
    Qc = min((Tskin-Tcold)/Rskin, COP*P)
    Qhot = P + Qc

    nf = max(2, int((W+fg)/(fg+t)))

    flow = CFM*0.0004719
    Aflow = (nf-1)*fg*H
    velocity = flow/Aflow

    Dh = 2*fg*H/(fg+H)
    Re = rho*velocity*Dh/mu

    if Re < 2300:
        Nu = 7.54
    else:
        Nu = 0.023*Re**0.8*0.71**0.4

    h = Nu*0.026/Dh

    Afin = 2*nf*L*H + L*W

    Rconv = 1/(h*Afin)
    Rair = 1/(2*rho*flow*Cp)

    Rhot = 0.002 + Rconv + Rair

    Thot = Tamb + Qhot*Rhot
    Tout = Tamb + Qhot/(rho*flow*Cp)

    Rreq = (Ttarget-Tamb)/Qhot

    return P, Qc, Qhot, Thot, Tout, Rhot, Rreq


# ---------------- INPUTS ----------------

st.sidebar.header("CASE 1 - Current Design")
N1 = st.sidebar.slider("Peltiers C1", 1, 6, 6)
I1 = st.sidebar.slider("Current C1", 1.0, 6.0, 6.0, 0.1)
sg1 = st.sidebar.slider("Skin Gap C1", 0.1, 5.0, 1.0, 0.1)
k1 = st.sidebar.slider("Interface k C1", 0.026, 2.0, 0.026, 0.01)
H1 = st.sidebar.slider("Fin Height C1", 10, 60, 35)
fg1 = st.sidebar.slider("Fin Gap C1", 2.0, 8.0, 4.0, 0.5)
F1 = st.sidebar.slider("Airflow C1", 30, 200, 100)

st.sidebar.header("CASE 2 - Improved")
N2 = st.sidebar.slider("Peltiers C2", 1, 6, 6)
I2 = st.sidebar.slider("Current C2", 1.0, 6.0, 4.0, 0.1)
sg2 = st.sidebar.slider("Skin Gap C2", 0.1, 5.0, 0.5, 0.1)
k2 = st.sidebar.slider("Interface k C2", 0.026, 2.0, 0.2, 0.01)
H2 = st.sidebar.slider("Fin Height C2", 10, 60, 45)
fg2 = st.sidebar.slider("Fin Gap C2", 2.0, 8.0, 4.0, 0.5)
F2 = st.sidebar.slider("Airflow C2", 30, 200, 120)

st.sidebar.header("CASE 3 - Optimized")
N3 = st.sidebar.slider("Peltiers C3", 1, 6, 6)
I3 = st.sidebar.slider("Current C3", 1.0, 6.0, 3.0, 0.1)
sg3 = st.sidebar.slider("Skin Gap C3", 0.1, 5.0, 0.2, 0.1)
k3 = st.sidebar.slider("Interface k C3", 0.026, 2.0, 1.0, 0.01)
H3 = st.sidebar.slider("Fin Height C3", 10, 60, 50)
fg3 = st.sidebar.slider("Fin Gap C3", 2.0, 8.0, 3.0, 0.5)
F3 = st.sidebar.slider("Airflow C3", 30, 200, 150)

cases = [
    (N1,I1,sg1,k1,H1,fg1,F1),
    (N2,I2,sg2,k2,H2,fg2,F2),
    (N3,I3,sg3,k3,H3,fg3,F3)
]

results = [model(*c) for c in cases]


# ---------------- RESULTS ----------------

st.subheader("Results")

cols = st.columns(3)

for i in range(3):

    P,Qc,Qhot,Thot,Tout,Rhot,Rreq = results[i]

    with cols[i]:

        st.markdown("### Case " + str(i+1))

        st.write("Power =", round(P,1), "W")
        st.write("Cooling =", round(Qc,1), "W")
        st.write("Hot Load =", round(Qhot,1), "W")

        st.write("T hot =", round(Thot,1),
                 "°C | Target ≤ 45")

        st.write("T out =", round(Tout,1),
                 "°C | Target ≤ 50")

        st.write("R hot =", round(Rhot,4),
                 "| Required ≤", round(Rreq,4))

        if Thot <= 45:
            st.success("PASS")
        else:
            st.error("FAIL")


# ---------------- GRAPH FUNCTION ----------------

def graph(x, ys, title, xlabel, ylabel, target=None):

    fig = go.Figure()

    for i in range(3):

        fig.add_trace(go.Scatter(
            x=x,
            y=ys[i],
            mode="lines",
            name="Case "+str(i+1),
            line=dict(color=colors[i], width=3)
        ))

    if target is not None:

        fig.add_hline(
            y=target,
            line_color="red",
            line_dash="dash",
            annotation_text="TARGET = "+str(round(target,4))
        )

    fig.update_layout(
        title=title,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        hovermode="x unified"
    )

    return fig


# ---------------- GRAPH 1 ----------------
# Current vs Cooling

x = np.linspace(1,6,60)
ys = []

for c in cases:

    N,I,sg,k,H,fg,F = c

    ys.append([
        model(N,a,sg,k,H,fg,F)[1]
        for a in x
    ])

st.plotly_chart(
    graph(x,ys,
          "Current vs Useful Cooling",
          "Current (A)",
          "Cooling (W)"),
    width="stretch"
)


# ---------------- GRAPH 2 ----------------
# Skin Gap vs Cooling

x = np.linspace(0.1,5,60)
ys = []

for c in cases:

    N,I,sg,k,H,fg,F = c

    ys.append([
        model(N,I,a,k,H,fg,F)[1]
        for a in x
    ])

st.plotly_chart(
    graph(x,ys,
          "Skin Gap vs Cooling",
          "Skin Gap (mm)",
          "Cooling (W)"),
    width="stretch"
)


# ---------------- GRAPH 3 ----------------
# Airflow vs Hot Temperature

x = np.linspace(30,200,60)
ys = []

for c in cases:

    N,I,sg,k,H,fg,F = c

    ys.append([
        model(N,I,sg,k,H,fg,a)[3]
        for a in x
    ])

st.plotly_chart(
    graph(x,ys,
          "Airflow vs Hot-side Temperature",
          "Airflow (CFM)",
          "Hot-side Temperature (°C)",
          45),
    width="stretch"
)


# ---------------- GRAPH 4 ----------------
# Fin Height vs Hot Temperature

x = np.linspace(10,60,60)
ys = []

for c in cases:

    N,I,sg,k,H,fg,F = c

    ys.append([
        model(N,I,sg,k,a,fg,F)[3]
        for a in x
    ])

st.plotly_chart(
    graph(x,ys,
          "Fin Height vs Hot-side Temperature",
          "Fin Height (mm)",
          "Hot-side Temperature (°C)",
          45),
    width="stretch"
)


# ---------------- GRAPH 5 ----------------
# Airflow vs R hot

x = np.linspace(30,200,60)
ys = []

for c in cases:

    N,I,sg,k,H,fg,F = c

    ys.append([
        model(N,I,sg,k,H,fg,a)[5]
        for a in x
    ])

# R hot target of current Case 1
Rtarget = results[0][6]

st.plotly_chart(
    graph(x,ys,
          "Airflow vs Thermal Resistance",
          "Airflow (CFM)",
          "R hot (K/W)",
          Rtarget),
    width="stretch"
)


# ---------------- GRAPH 6 ----------------
# Airflow vs Outlet Temperature

ys = []

for c in cases:

    N,I,sg,k,H,fg,F = c

    ys.append([
        model(N,I,sg,k,H,fg,a)[4]
        for a in x
    ])

st.plotly_chart(
    graph(x,ys,
          "Airflow vs Outlet Air Temperature",
          "Airflow (CFM)",
          "Outlet Temperature (°C)",
          50),
    width="stretch"
)