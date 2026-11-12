"""Cosine attention: scores are scaled cosine similarities of queries and keys.

Queries and keys are L2-normalized after rotary position encoding, so a score
depends on direction only and each head learns one scale in place of the usual
1/sqrt(head_dim). This file is all Lab needs: it is not edited.

Torch is imported inside ``build`` so that Lab can validate a config that names
this kind without loading Torch.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from klab.components import Component


class CosineParams(BaseModel):
    """Settings under ``attention.params`` for ``kind: cosine``."""

    model_config = ConfigDict(extra="forbid")

    initial_scale: float = Field(default=10.0, gt=0)
    learned_scale: bool = True


def build(model, attention, params: CosineParams):
    import math

    import torch
    from torch import nn

    from klab.model.cache import AttentionKVCache
    from klab.model.rope import RoPE

    class CosineAttention(nn.Module):
        # Naming a cache backend and offering create_cache/forward_cached lets
        # generation decode incrementally instead of recomputing the prefix.
        cache_backend = "cosine"

        def __init__(self) -> None:
            super().__init__()
            hidden = model.hidden_dim
            self.num_heads = model.num_heads
            self.head_dim = hidden // model.num_heads
            self.max_seq_len = model.max_seq_len
            self.q_proj = nn.Linear(hidden, hidden, bias=False)
            self.k_proj = nn.Linear(hidden, hidden, bias=False)
            self.v_proj = nn.Linear(hidden, hidden, bias=False)
            self.out_proj = nn.Linear(hidden, hidden, bias=False)
            self.rope = RoPE(self.head_dim, attention.rope_base)
            log_scale = torch.full(
                (self.num_heads, 1, 1), math.log(params.initial_scale)
            )
            if params.learned_scale:
                self.log_scale = nn.Parameter(log_scale)
            else:
                self.register_buffer("log_scale", log_scale, persistent=False)

        @property
        def cache_layout(self) -> tuple[int, int, int]:
            return self.num_heads, self.head_dim, self.head_dim

        def _heads(self, projection: nn.Linear, x):
            batch, length, _ = x.shape
            return projection(x).view(
                batch, length, self.num_heads, self.head_dim
            ).transpose(1, 2)

        def _unit(self, projection: nn.Linear, x, offset: int = 0):
            rotated = self.rope(self._heads(projection, x), position_offset=offset)
            return nn.functional.normalize(rotated, dim=-1)

        def _attend(self, query, key, value, allowed):
            scores = self.log_scale.exp() * (query @ key.transpose(-2, -1))
            scores = scores.masked_fill(~allowed, float("-inf"))
            weights = torch.softmax(scores.float(), dim=-1).to(value.dtype)
            output = (weights @ value).transpose(1, 2)
            return self.out_proj(output.reshape(output.shape[0], output.shape[1], -1))

        def forward(self, x):
            length = x.shape[1]
            if length > self.max_seq_len:
                raise ValueError("sequence length exceeds configured attention context")
            allowed = torch.ones(
                length, length, dtype=torch.bool, device=x.device
            ).tril()
            return self._attend(
                self._unit(self.q_proj, x),
                self._unit(self.k_proj, x),
                self._heads(self.v_proj, x),
                allowed,
            )

        def create_cache(self, batch, capacity, *, device, dtype) -> AttentionKVCache:
            shape = (batch, self.num_heads, capacity, self.head_dim)
            return AttentionKVCache(
                key=torch.empty(shape, device=device, dtype=dtype),
                value=torch.empty(shape, device=device, dtype=dtype),
                length=0,
                position=0,
            )

        def forward_cached(self, x, cache: AttentionKVCache):
            length, offset = x.shape[1], cache.position
            if offset + length > self.max_seq_len:
                raise ValueError("sequence length exceeds configured attention context")
            cache.append(
                self._unit(self.k_proj, x, offset),
                self._heads(self.v_proj, x),
                position=offset + length,
            )
            positions = torch.arange(cache.length, device=x.device)
            allowed = positions[None, :] <= positions[offset:, None]
            output = self._attend(
                self._unit(self.q_proj, x, offset),
                cache.key[:, :, : cache.length],
                cache.value[:, :, : cache.length],
                allowed,
            )
            return output, cache

    return CosineAttention()


COMPONENT = Component("attention", "cosine", build, params=CosineParams)
