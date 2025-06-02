# type: ignore
import torch as t
import transformer_lens as tl


@t.no_grad()
def solve_chall_1(model: tl.HookedTransformer, max_new_tokens: int = 32):
    tokens = model.to_tokens("User: 404CTF{")
    output_ids = model.generate(tokens, max_new_tokens=max_new_tokens, temperature=0)
    print(model.to_string(output_ids[0]))


@t.no_grad()
def solve_chall_2(
    model: tl.HookedTransformer, nb_layers: int = 4, max_new_tokens: int = 32
):
    """
    Principe de base de Logit Lens: https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens

    Utilisation du unembedding sur une couche intermédiaire.
    """
    for i in range(nb_layers):
        prompt = "User: 404CTF{"

        for _ in range(max_new_tokens):
            prompt += str(
                model.to_string(
                    t.argmax(
                        (model.forward(prompt, stop_at_layer=-1 - i) @ model.W_U)[
                            :, -1
                        ],
                        dim=-1,
                    )
                )
            )
        print(prompt)


@t.no_grad()
def solve_chall_3(
    gorfoustral: tl.HookedTransformer,
    gpt: tl.HookedTransformer,
    flag: str = "User: 404CTF{",
    target_layer: int = 12,
    topk: int = 10,
):
    """
    Utilisation du modèle diffing : en faisant la différence entre le modèle de base et celui finetuné, on récupère le "rajout", qui pour le coup, suffit à récupérer le drapeau dés la moitié du modèle.

    ! il est supposé que l'on connaisse la structure du drapeau avec les _ à chaque fin de mot et que l'on avance pas à pas !
    """
    tokens = gorfoustral.to_tokens(flag, prepend_bos=True)
    _, gorfoustral_cache = gorfoustral.run_with_cache(tokens)
    _, gpt_cache = gpt.run_with_cache(tokens)

    residual_diff = (
        gorfoustral_cache["resid_post", target_layer][0]
        - gpt_cache["resid_post", target_layer][0]
    )
    tokens_diff = residual_diff[-1] @ gorfoustral.W_U
    print(gorfoustral.to_string(tokens_diff.topk(k=topk).indices.unsqueeze(-1)))
