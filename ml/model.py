import torch
from torch import nn

N_TYPES = 13


class FightQ(nn.Module):
    def __init__(self, n_unit, n_game, width=16, hidden=16, n_teams=0, team_dim=4):
        super().__init__()
        self.phi_x = nn.Linear(n_unit, width)
        self.phi_t = nn.Embedding(N_TYPES, width)
        self.team = nn.Embedding(n_teams, team_dim) if n_teams else None
        ctx = 3 * width + n_game + (team_dim if n_teams else 0)
        self.engage = nn.Sequential(nn.Linear(width + ctx, hidden), nn.ReLU(), nn.Linear(hidden, 1))
        self.stay = nn.Sequential(nn.Linear(ctx, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def phi(self, x, t):
        return torch.relu(self.phi_x(x) + self.phi_t(t))

    def forward(self, b):
        me = self.phi(b["self_x"], b["self_t"])
        allies = (self.phi(b["ally_x"], b["ally_t"]) * b["ally_m"][..., None]).sum(1)
        enemy_each = self.phi(b["enemy_x"], b["enemy_t"]) * b["enemy_m"][..., None]
        parts = [me, allies, enemy_each.sum(1), b["game_x"]]
        if self.team is not None:
            parts.append(self.team(b["team_id"]))
        ctx = torch.cat(parts, -1)
        per_enemy = torch.cat([enemy_each, ctx[:, None].expand(-1, enemy_each.shape[1], -1)], -1)
        return self.engage(per_enemy).squeeze(-1), self.stay(ctx).squeeze(-1)


def q_loss(q_engage, q_stay, b):
    taken = b["engaged_m"].float()
    n_taken = taken.sum(1)
    y = b["label"]
    engage_err = ((q_engage - y[:, None]) ** 2 * taken).sum(1) / n_taken.clamp(min=1)
    stay_err = (q_stay - y) ** 2
    return torch.where(n_taken > 0, engage_err, stay_err).mean()
