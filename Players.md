# RL Player Strategy Integration Plan

This document outlines the design and implementation plan for adding ten distinct AI player archetypes into the Monopoly environment. Each player type has a defined behavioural profile, reward structure, feature prioritisation, and persistent RL model.

---

## 1. Overview

The aim is to train 10 distinct RL agents, each embodying a unique strategic philosophy. During training, each game will randomly assign **4–6 agents** from this pool. Each agent maintains:

- Its own model file (local checkpoint)
- Its own reward shaping
- Its own action-priority heuristics
- Its own persistent training history

The environment remains identical for all agents; only the **policy** differs.

---

## 2. Player Types Implemented

1. Alice — Money maximiser  
2. Bob — High-value property developer  
3. Charlie — Infrastructure (utilities + railways) collector  
4. Dee — Trade specialist  
5. Ethel — Property hoarder  
6. Frankie — Development maximiser  
7. Greta — Monopoly completer  
8. Harry — Resource denial/blocker  
9. Irene — Balanced ROI investor  
10. Jack — Hyper-aggressive destabiliser  

Each is defined in `PLAYER_BEHAVIOURS.json`.

---

## 3. Architecture

### 3.1 Agent Structure

Each agent will follow a consistent interface:

```python
class RLPlayer:
    def __init__(self, behaviour_profile):
        self.behaviour = behaviour_profile
        self.model = load_or_init_model(self.behaviour["id"])
3.2 Local Model Saving
Each agent writes to:

pgsql
Copy code
models/<player_id>/
    policy.pt
    replay_buffer.pkl
    metadata.json
Training is incremental across games.

4. Reward Shaping
Each profile defines weights for the following metrics:

Cash change

Expected rent yield of owned tiles

Property acquisition count

Monopoly completion or monopoly blocking

Trade success metrics

Development level

Example:

makefile
Copy code
reward = (w_cash * Δcash
          + w_rent * expected_rent
          + w_props * property_count
          + w_dev * development_level
          + w_trade * trade_value
          + w_mono * monopoly_delta)
Weights come directly from the JSON.

5. Action Spaces
Agents choose from:

Buy tile

Auction strategy

Build houses/hotels

Trade offers

Trade acceptance

Mortgage / unmortgage

Liquidation (when broke)

Each action is biased by the profile:

Alice biases “save cash”

Frankie biases “build houses”

Charlie biases “buy rail/utility”

Greta biases “trade for sets”

Harry biases “buy tiles others need”

6. State Representation
Recommended features:

Financial
Player cash

Opponents’ cash distributions

Debt/mortgage status

Board Control
Ownership of each tile

Development levels

Missing tiles to complete monopoly

Risk Metrics
Distance to high-rent zones

Chance of hitting opponent monopolies

Opportunity Metrics
Tiles for sale

Trade opportunities

Threatened monopolies

7. Game Simulation Loop
For each training game:

Randomly select 4–6 players from the pool.

Initialise models for those players.

Step through the game loop.

Collect trajectories for each agent.

Apply reward shaping individually.

Update local models after each game.

Save checkpoints.

8. Evaluation
Track per-agent:

Win rate

Bankruptcy frequency

Mean game length

Monopoly completion rate

Average cash position

Average rent income

Trade profit margins

Run leagues of 10k+ games.

9. Roadmap
Phase 1
Finalise tile ordering

Implement core rules

Add JSON-defined agent behaviours

Set up save/load system for models

Phase 2
Add RL training loops (PPO recommended)

Add trade negotiation network

Add development optimisation

Phase 3
Run multi-agent tournaments

Produce strategy evolution dashboards
