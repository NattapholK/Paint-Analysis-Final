# Paint Thermal Analysis (complete)

Run:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python analyze.py
```
Composite score = 0.30*mean + 0.40*median + 0.30*p75 − 0.10*std + 0.02*sqrt(n)
mean = average ΔT (outside − inside)

median = central tendency

p75 = upper quartile (how well the formula performs in best cases)

std = stability penalty (lower std = more stable)

n = sample size adjustment


#Result

Both Daily outdoor tests and UVC room tests show that:

Formula 4 (F4) achieved the highest composite score

F4 consistently reduced interior temperature more effectively than other formulas

Confirms the report’s conclusion that F4 is the best performing eco-paint formula