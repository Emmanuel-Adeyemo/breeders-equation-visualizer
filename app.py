import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Import your simulation module
import simulate as sim

st.set_page_config(
    page_title="Breeder's Equation Explorer",
    layout="wide"
)

# scenarios
PRESETS = {
    '-- choose a preset --': None,
    'High h2, strong selection': {'h2': 0.6, 'p': 0.1},
    'Low h2, strong selection': {'h2': 0.15, 'p': 0.1},
    'High h2, weak selection': {'h2': 0.6, 'p': 0.5},
    'Many generations': {'h2': 0.4, 'p': 0.1, 'n_gen': 20, 'shrink': True},
}

st.title("Breeder's Equation Explorer")
st.latex(r"R = h^2 S = i h^2 \sigma_P")

for key, default in [
    ('h2_slider', 0.40),
    ('p_slider', 0.2),
    ('n_gen_slider', 10),
    ('shrink_checkbox', False)
    ]:
    if key not in st.session_state:
        st.session_state[key] = default

def apply_preset():
    preset = PRESETS[st.session_state.preset_choice]
    if preset is None:
        return
    if 'h2' in preset:
        st.session_state.h2_slider = preset['h2']
    if 'p' in preset:
        st.session_state.p_slider = preset['p']
    if 'n_gen' in preset:
        st.session_state.n_gen_slider = preset['n_gen']
    if 'shrink' in preset:
        st.session_state.shrink_checkbox = preset['shrink']

st.selectbox(
    'Preset scenario', list(PRESETS.keys()),
    key='preset_choice', on_change=apply_preset,
)

# preset_choice = st.selectbox('Preset scenario', list(PRESETS.keys()))
# preset = PRESETS[preset_choice]
#
# if 'h2' not in st.session_state:
#     st.session_state.h2 = 0.4
# if 'p' not in st.session_state:
#     st.session_state.p = 0.2
# if 'n_gen' not in st.session_state:
#     st.session_state.n_gen = 10
# if 'shrink' not in st.session_state:
#     st.session_state.shrink = False

# if preset is not None:
#     st.session_state.h2 = preset.get('h2', st.session_state.h2)
#     st.session_state.p = preset.get('p', st.session_state.p)
#     st.session_state.n_gen = preset.get('n_gen', st.session_state.n_gen)
#     st.session_state.shrink = preset.get('shrink', st.session_state.shrink)


# shared control
mu0 = 100
sd_p0 = 15
col_control1, col_control2= st.columns(2)
with col_control1:
    h2 = st.slider(
        'Narrow-sense heritability (h²)', min_value=0.0, max_value=1.0, step=0.01, key='h2_slider'
    )

with col_control2:
    p = st.slider(
        'Proportion selected (p)', min_value=0.01, max_value=0.99,  step=0.01, key='p_slider'
    )
st.divider()

# Single generation
st.header('Panel A: One generation of selection')

trunc = sim.calc_truncation_point(mu0, sd_p0, p)
i_val = sim.selection_intensity(p)
S = sim.selection_differential(sd_p0, p)
R = sim.calculate_response(h2, sd_p0, p)
curves = sim.get_curve_params(mu0, sd_p0, R)


x = curves['x']
y_parent = curves['y_orig']
y_offspring = curves['y_child']
mu_offspring = curves['mu_child']
mu_s = mu0 + S # mean of selected parents

# fig_a = go.Figure()

fig_a = make_subplots(
    rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.22, subplot_titles=(
        "Parental Population",
        "Offspring Population",
    ),
)


# parent generation curve - top plot
fig_a.add_trace(
    go.Scatter(x=x, y=y_parent, mode='lines', name='Parent Distribution', line=dict(color='#1f77b4', width=2)), row=1, col=1,)

# shade selected area
mask = x >= trunc
x_selected = x[mask]
y_selected = y_parent[mask]
fig_a.add_trace(go.Scatter(
    x=curves['x'][mask], y=curves['y_orig'][mask], mode='lines', fill='tozeroy', name='Selected individuals',
    line=dict(color='rgba(0,0,0,0)'), fillcolor='rgba(76,114,176,0.35)', showlegend=True
), row=1, col=1,)

fig_a.add_vline(x=mu0, line_dash='dash', line_color='gray', annotation_text='μ₀', row=1, col=1)
fig_a.add_vline(x=trunc, line_dash='dot', line_color='red', annotation_text='Cutoff', row=1, col=1)
fig_a.add_vline(x=mu_s, line_dash='dash', line_color='blue', annotation_text='μ_s', row=1, col=1)

# offspring generation curve - bottom plot
fig_a.add_trace(
    go.Scatter(x=x, y=y_parent, mode='lines', name='Base Reference',
               line=dict(color='gray', width=1, dash='dash')),
    row=2, col=1,
)
fig_a.add_trace(
    go.Scatter(x=x, y=y_offspring, mode='lines', name='Offspring Distribution',
               line=dict(color='#2ca02c', width=2)),
    row=2, col=1,
)

fig_a.add_vline(x=mu0, line_dash='dash', line_color='gray', row=2, col=1)
fig_a.add_vline(x=mu_offspring, line_dash='dash', line_color='green', annotation_text='μ₁ = μ₀ + R', row=2, col=1)



# for x_val, label, color in [
#     (mu0, 'Parent mean (μ)', '#4C72B0'),
#     (trunc, 'Truncation point', '#55A868'),
#     (curves['mu_child'], 'Offspring mean', '#DD8452'),
#     ]:
#     fig_a.add_vline(x=x_val, line=dict(color=color, dash='dot', width=1.5))
#     fig_a.add_annotation(x=x_val, y=max(curves['y_orig'].max(), curves['y_child'].max()) * 1.05,
#                          text=label, showarrow=False, font=dict(size=11, color=color))
#
fig_a.update_layout(
    height=560,
    margin=dict(l=20, r=20, t=50, b=20),
    hovermode='x unified',
    # xaxis_title='Phenotypic value',
    # yaxis_title='Density',
    # legend=dict(orientation='h', yanchor='bottom', y=1.1, xanchor='left', x=0),
)
fig_a.update_xaxes(title_text='Phenotypic Value', row=2, col=1)
fig_a.update_yaxes(title_text='Density', row=1, col=1)
fig_a.update_yaxes(title_text='Density', row=2, col=1)


st.plotly_chart(fig_a, use_container_width=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric('Selection intensity (i)', f'{i_val:.3f}')
m2.metric('Selection differential (S)', f'{S:.2f}')
m3.metric('Response to selection (R)', f'{R:.2f}')
m4.metric('Offspring mean', f'{mu_offspring:.2f}')

st.caption(
    'The shaded region is the selected fraction of the parent population. '
    "S is the gap between the selected group's mean and the population mean. "
    'R is the fraction of that gap (h²) that shows up in the offspring generation mean.'
)

st.divider()

#multi generations
# ------------
st.header('Panel B: Response across generations')

col_b1, col_b2 = st.columns([1, 1])
with col_b1:
    n_gen = st.slider(
        'Number of generations', min_value=1, max_value=30,
        step=1, key='n_gen_slider',
    )
with col_b2:
    shrink = st.checkbox(
        'Shrink phenotypic variance each generation',
        key='shrink_checkbox',
    )
# with col_b3:
#     shrink_mode = st.radio(
#         'Plateau strength',
#         options=['Pronounced (ties decay to selection intensity)', 'Gentle (fixed % decay)'],
#         key='shrink_mode_radio',
#         disabled=not shrink,
#         help="'Pronounced' makes variance loss scale with how hard you're selecting -- "
#              "closer to the classic diminishing-returns teaching curve. 'Gentle' is a "
#              "simple fixed percentage decline per generation, which flattens much more slowly.",
#     )

shrink_mode = 'Pronounced'
mode = "intensity" if shrink_mode.startswith("Pronounced") else "fixed"
default_rate = 0.06 if mode == "intensity" else 0.90
rate_label = 'Decay rate (higher = faster plateau)' if mode == 'intensity' else 'Shrink factor per generation'
rate_min, rate_max, rate_step = (0.01, 0.15, 0.01) if mode == 'intensity' else (0.80, 0.99, 0.01)


shrink_rate = st.slider(
    rate_label, min_value=rate_min, max_value=rate_max,
    value=default_rate, step=rate_step, key=f'shrink_rate_{mode}',
    disabled=not shrink,
)

# Always compute both trajectories so students can compare constant-variance
# (linear) vs. shrinking-variance (decelerating) side by side, regardless of
# the checkbox -- this makes the difference the checkbox controls unmistakable.
traj_const = sim.run_generations(mu0, sd_p0, h2, p, n_gen, shrink_variance=False)
traj_shrink = sim.run_generations(
    mu0, sd_p0, h2, p, n_gen,
    shrink_variance=True, shrink_factor=shrink_rate, shrink_mode=mode,
)

fig_b = go.Figure()
fig_b.add_trace(go.Scatter(
    x=traj_const['generation'], y=traj_const["mu"], mode='lines+markers',
    name='Constant variance (linear)',
    line=dict(color="#4C72B0", width=3, dash="dot" if shrink else 'solid'),
    opacity=1.0 if shrink else 1.0,
))
if shrink:
    fig_b.add_trace(go.Scatter(
        x=traj_shrink['generation'], y=traj_shrink['mu'], mode='lines+markers',
        name='Shrinking variance (decreasing)',
        line=dict(color='#DD8452', width=3),
    ))

fig_b.update_layout(
    height=420,
    xaxis_title='Generation',
    yaxis_title='Population mean',
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='left', x=0),
    margin=dict(t=60),
)
st.plotly_chart(fig_b, use_container_width=True)

if shrink:
    final_const = traj_const['mu'][-1]
    final_shrink = traj_shrink['mu'][-1]
    st.metric(
        "Gain 'lost' to the plateau effect by the final generation",
        f'{final_const - final_shrink:.2f} phenotypic units',
    )
    # st.caption(
    #     'Phenotypic variance shrinks per generation of selection by shrink factor to mimic real-life scenario. '
    # )
    
# else:
#     st.caption(
#         'Constant phenotypic variance and heritability creates a constant response per generation. Tick box above to overlay '
#         'with shrinking phenotypic variance per generation.'
#     )

st.divider()


# panel C - realized h2
st.header('Panel C: Realized Heritability -- h² after selection ')


for key, default in [
    ('realized_true_h2_slider', 0.40),
    ('realized_n_offspring_slider', 50),
    ('realized_n_reps_slider', 200)
    ]:
    if key not in st.session_state:
        st.session_state[key] = default

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    true_h2_c = st.slider(
        'True h² used to generate the data (unknown to the breeder in practice)',
        min_value=0.0, max_value=1.0, step=0.01, key='realized_true_h2_slider'
    )

with col_c2:
    n_offspring_c = st.slider(
        'Offspring measured per experiment', min_value=5, max_value=500, step=5,
        key='realized_n_offspring_slider',
        help='More offspring measured, less noisy estimate of R, and h².'


    )

with col_c3:
    n_reps_c = st.slider(
        'Number of independent replicate experiments', min_value=1, max_value=1000, step=10,
        key='realized_n_reps_slider',
        help='Each replicate reruns the same experiments (same true h², same no_of_offsprings) with fresh random sampling.'
             'More replicates build a clearer picture of how much a single realized h² estimate can be trusted.'
    )


if 'realized_seed' not in st.session_state:
    st.session_state.realized_seed = 785

col_resim_c, _ = st.columns([1, 3])
with col_resim_c:
    if st.button('Resimulate experiments'):
        st.session_state.realized_seed += 1

rng_c = np.random.default_rng(st.session_state.realized_seed)

realized = sim.simulate_realized_heritability(
    true_h2_c, sd_p0, p, n_offspring_c, n_reps_c, rng_c
)

h2_hat = realized['h2_hat']
h2_hat_valid = h2_hat[~np.isnan(h2_hat)]

fig_c = go.Figure()

fig_c.add_trace(go.Histogram(
    x=h2_hat_valid, nbinsx=40, name='h² across replicates', marker_color='#4c72b0', opacity=0.75
))
fig_c.add_vline(
    x=true_h2_c, line=dict(color='#55a868', width=3, dash='dash'), annotation_text='True h²', annotation_position='top'
)

if n_reps_c > 1:
    fig_c.add_vline(
        x=float(np.nanmean(h2_hat)), line=dict(color='#dd8452', width=2, dash='dot'),
        annotation_text='Mean h² hat', annotation_position='bottom',
    )

fig_c.update_layout(
    height=420,
    xaxis_title='Realized heritability estimate',
    yaxis_title='Count of replicate experiments',
    margin=dict(t=40),
    showlegend=False
)

st.plotly_chart(fig_c, use_container_width=True)

mc1, mc2, mc3 = st.columns(3)
mc1.metric('True h²', f'{true_h2_c:.3f}')
mc2.metric('Mean h² hat across replicates', f'{np.nanmean(h2_hat):.3f}' if n_reps_c > 1 else f'{h2_hat_valid[0]:.3f}')
mc3.metric("SD of h² across replicates", f"{np.nanstd(h2_hat):.3f}" if n_reps_c > 1 else "n/a (only 1 rep)")

st.caption(
    "h² estimates from realized selection response are usually "
    "reported as an average over multiple cycles or lines, not trusted from a single generation alone."
)


