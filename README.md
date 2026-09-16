Response to Selection — Teaching App
 
Streamlit app for teaching breeder's equation/response to selection in a graduate plant breeding course at Auburn University in Fall 2026.

### Parent-Offspring Regression Simulator (`app.py`)
Teaches heritability as the slope of the offspring-on-midparent regression line.
 
- **Panel A** — set additive genetic variance (VA) and environmental variance (VE) with sliders; see the resulting phenotypic variance decomposition and true h².
- **Panel B** — simulated parent-offspring family data, with a fitted regression line and a true-h² reference line, so students can see the fitted slope jitter around the true value due to sampling noise. Includes a "resimulate" button and an "offspring per family" slider to show how averaging reduces noise without changing the true h².
Core simulation logic lives in `simulate.py`

## Running locally
 
```bash
pip install -r requirements.txt
streamlit run app.py              # Breeder's Equation Explorer
```

### App deployed on Streamlit
aub.ie/breeders