# Pitch Skeleton — Demo Day Prep (Block D Workshop Artifact)

**Team:** Group 18 — Alonso Cárdenas, Benjamín Sánchez  
**Date:** May 13, 2026  
**Audience:** Aston Martin Engineering Strategy Desk (simulated)

> **Note:** This file is a Block D workshop artifact for Demo Day preparation (Mon May 18). It is not graded as part of Hito 2, but is committed today while the evidence is fresh.

---

## Slide 1 — The Decision Problem

**Title:** *"Should Aston Martin run a 1-stop or 2-stop strategy at a permanent circuit when starting P4–P6?"*

**Hook:**  
In 2024, a strategist relying only on points-finish probability cannot tell the difference between a 1-stop and 2-stop strategy at Bahrain — they're equivalent for scoring points. But they are **not equivalent for the podium**. The gap is 8.7 percentage points, and it's invisible without the right model.

**Problem statement:**  
A strategy desk managing a front-of-midfield car (Aston Martin 2024 tier) has one tool today: gut feel informed by historical pace data. There is no pre-race, scenario-aware probability estimate that separates *"we'll score points either way"* from *"only 2-stop gives us a real podium shot."*

**Our tool solves this** by delivering two calibrated probabilities — P(top10) and P(top3) — for any planned strategy the team declares before the race.

---

## Slide 5 — The Verdict

**Team verdict sentence (written before submission, while evidence is fresh):**

> *"At a permanent circuit with a P5 midfield starter, a 1-stop and 2-stop planned strategy are statistically indistinguishable for points-scoring (ΔP = −0.006), but the 2-stop strategy delivers +8.7 percentage points of podium probability — a difference our is_top10 model cannot see and only our is_top3 expansion reveals."*

**What the model adds beyond a heuristic:**  
A strategy desk without this tool would apply the heuristic "protect track position → 1-stop." For points accumulation, that heuristic is correct. For podium challenge, it costs Aston Martin roughly 1 podium attempt per 11-12 races of this type where they choose 1-stop instead of 2-stop.

**Model limitations the audience must know:**  
1. `n_stops` is the **planned** stop count — not a causal guarantee. The model captures historical associations, not controlled experiments.  
2. Street circuits are outside the model's reliable operating range (Brier +36%).  
3. The recommendation is "2-stop for podium" — but track evolution, safety car timing, and rival strategy updates during the race may override it.

**Call to action:**  
Deploy the two-target probability display in the strategy desk's pre-race debrief tool for permanent and hybrid circuits, for P3–P8 grid positions, for midfield-front tier cars. Flag street circuits as "manual assessment only." Retrain at the start of each season.
