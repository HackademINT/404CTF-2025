"""
Le challenge nécessite la même librairie que les précédent : Transformer Lens.

Garanties :
    - Dans chaque journal, la moitié des phrases sont tatouées, la moitié ne le sont pas.
    - La taille du masque est toujours 10 (valeur par défaut).
    - Le début du tatouage est toujours avant le 20e jeton. Autrement dit, la génération commence à partir d'un prompt de base et le modèle complète, il est garanti que les prompts de base font tous moins de 20 jetons, donc pour une phrase tatouée p et sa liste de jetons x, il est garanti que x[20:] est tatoué.
    - La température varie en fonction des challenges, elle se situe toujours entre 1 et 3.3
    - Le drapeau (la clef_secrète), est pour chaque journal un entier entre 1 et 99999.
    - Le drapeau final est 404CTF{clef_secrète_journal35clef_secrète_journal34clef_secrète_journal33}, par exemple : 404CTF{123451234512345}.
"""

import torch as t
import transformer_lens as tl
from torch import Tensor

TEMPÉRATURE = 3.3
TAILLE_MASQUE = 10


def load_model_vague_2(
    device: t.device | str = "cuda", dtype: t.dtype = t.float16
) -> tl.HookedTransformer:
    """
    Load le modèle sur GPU : device = "cuda", dtype = t.float16
    Load le modèle sur CPU : device = "cpu", dtype = t.bfloat16
    """
    model = tl.HookedTransformer.from_pretrained_no_processing(
        "tiny-stories-instruct-33M", dtype=dtype, device=device
    )
    return model


def cryptage_très_puissant(
    clef_très_secrète: int, précédent_token: int, précédent_du_précédent_token: int
) -> int:
    return (précédent_token * clef_très_secrète + précédent_du_précédent_token) % 50033


def récupérer_le_masque(seed: int) -> Tensor:
    g = t.Generator()
    g.manual_seed(seed)
    perm = t.randperm(2 * TAILLE_MASQUE, generator=g)
    mask = t.zeros(2 * TAILLE_MASQUE, dtype=t.bool)
    mask[perm[:TAILLE_MASQUE]] = True
    return mask


def génération_avec_tatouage(
    model: tl.HookedTransformer,
    prompt: str,
    clef_secrète: int,
    max_nouveaux_jetons: int = 100,
    température: float = 3.3,
    verbose: bool = False,
) -> str:
    for _ in range(max_nouveaux_jetons):
        tokens = model.to_tokens(prompt)
        logits = model(tokens)
        values, indices = logits[0, -1, :].topk(k=2 * TAILLE_MASQUE)

        if verbose:
            print(f"Choix initiaux: {model.to_string(indices)}")

        seed = cryptage_très_puissant(
            clef_secrète, int(tokens[0, -1].item()), int(tokens[0, -2].item())
        )
        mask = récupérer_le_masque(seed)
        values, indices = values[mask], indices[mask]

        if verbose:
            print(f"Masque: {mask}, \nNouveaux choix: {model.to_string(indices)}")

        probs = t.softmax(values / température, dim=-1)
        next_token = indices[t.multinomial(probs, 1)]

        if verbose:
            print(f"Jeton choisi: {model.to_string(next_token)}")

        if next_token == model.to_single_token(model.tokenizer.eos_token):  # type: ignore
            break

        prompt += str(model.to_string(next_token))

    return prompt


def génération_sans_tatouage(
    model: tl.HookedTransformer,
    prompt: str,
    max_nouveaux_jetons: int = 100,
    température: float = 3.3,
) -> str:
    for _ in range(max_nouveaux_jetons):
        tokens = model.to_tokens(prompt)
        logits = model(tokens)
        values, indices = logits[0, -1, :].topk(k=2 * TAILLE_MASQUE)

        probs = t.softmax(values / température, dim=-1)
        next_token = indices[t.multinomial(probs, 1)]

        if next_token == model.to_single_token(model.tokenizer.eos_token):  # type: ignore
            break

        prompt += str(model.to_string(next_token))

    return prompt
