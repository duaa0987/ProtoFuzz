"""Safe, deterministic mutation strategies for byte-oriented protocol inputs."""
from __future__ import annotations
import random

BOUNDARIES = (0, 1, 2, 127, 128, 254, 255)

def bit_flip(data: bytes, rng: random.Random) -> bytes:
    if not data:
        return b"\x01"
    out = bytearray(data)
    index = rng.randrange(len(out))
    bit = 1 << rng.randrange(8)
    out[index] ^= bit
    return bytes(out)

def byte_repetition(data: bytes, rng: random.Random) -> bytes:
    if not data:
        return b"\x00" * 2
    index = rng.randrange(len(data))
    count = rng.choice((2, 3, 4, 8))
    return data[:index] + data[index:index+1] * count + data[index+1:]

def truncation(data: bytes, rng: random.Random) -> bytes:
    if not data:
        return b""
    cut = rng.randrange(len(data))
    return data[:cut]

def boundary_values(data: bytes, rng: random.Random) -> bytes:
    if not data:
        return bytes([rng.choice(BOUNDARIES)])
    out = bytearray(data)
    index = rng.randrange(len(out))
    out[index] = rng.choice(BOUNDARIES)
    return bytes(out)

def dictionary_mutation(data: bytes, rng: random.Random, words: list[bytes]) -> bytes:
    if not words:
        return data
    token = rng.choice(words)
    index = rng.randrange(len(data) + 1)
    return data[:index] + token + data[index:]

MUTATORS = {
    "bit_flip": bit_flip,
    "byte_repetition": byte_repetition,
    "truncation": truncation,
    "boundary_values": boundary_values,
}
