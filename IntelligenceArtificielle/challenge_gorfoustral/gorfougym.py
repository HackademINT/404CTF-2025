import os
import random
from typing import Dict, List, Optional

import torch as t
import transformer_lens as tl

# À retirer si vous souhaitez utiliser des gradients (non nécessaire)
t.set_grad_enabled(False)

#################################################
# Utilitaires                                   #
#################################################


def load_model(
    from_: Optional[str] = None, device: t.device = "cpu", dtype: t.dtype = t.bfloat16
):
    """
    Pour load le modèle sur CPU (default) :
        device = "cpu"
        dtype = t.bfloat16

    Pour load le modèle sur GPU :
        device = "cuda"
        dtype = t.float16 ou t.float32
    """
    model = tl.HookedTransformer.from_pretrained_no_processing(
        "gpt2-medium", dtype=dtype, device=device
    )

    if from_ is not None:
        model.load_state_dict(t.load(from_, map_location=device))

    return model


def load_model_vague_2(device: t.device = "cuda", dtype: t.dtype = t.float16):
    model = tl.HookedTransformer.from_pretrained_no_processing(
        "tiny-stories-instruct-33M", dtype=dtype, device=device
    )
    return model


def chat_template(user: str, assistant: Optional[str] = None) -> str:
    """
    Le modèle a été entraîné sur le chat template suivant :

    ```
    User: {l'entrée utilisateur : le flag}
    Assistant: {la réponse : True ou False}
    ```

    Par exemple :
    ```
    User: 404CTF{des_coureurs_des_vents}
    Assistant: False
    ```
    """
    return f"User: {user}\nAssistant:{' ' + assistant if assistant is not None else ''}"


@t.no_grad()
def test_flag(model: tl.HookedTransformer, flag: str):
    """
    Cette fonction appelle le modèle avec le chat template et retourne uniquement la réponse de l'assistant : True ou False
    """
    tokens = model.to_tokens(chat_template(flag))
    output_ids = model.generate(tokens, max_new_tokens=1, temperature=0)
    return model.to_string(output_ids[0, -1])  # type: ignore


#################################################
# Training utilisé pour créer les challenges    #
#################################################


POSSIBLE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:,.<>?/"
PAD_TOKEN = -100
UNDERSCORE_TOKEN = 62


def get_random_char_perturbation(
    flag: str, min_flips: int = 2, max_flips: int = 20
) -> str:
    max_flips = min(len(flag), max_flips)
    perturbated_flag = list(flag)

    for x in random.choices(range(len(flag)), k=random.randint(min_flips, max_flips)):
        perturbated_flag[x] = POSSIBLE_CHARS[
            (POSSIBLE_CHARS.index(flag[x]) + random.randint(0, len(POSSIBLE_CHARS) - 1))
            % len(POSSIBLE_CHARS)
        ]

    return "".join(perturbated_flag)


def get_random_token_perturbation(
    flag: str,
    model: tl.HookedTransformer,
    min_flips: int = 1,
    max_flips: int = 3,
    max_iterations: int = 100,
):
    success = chat_template(flag)
    success_str_tokens = model.to_str_tokens(success)
    success_tokens = model.to_tokens(success)[0]

    b, a = success_str_tokens.index("{") + 1, success_str_tokens.index("}")  # type: ignore

    middle_tokens = success_tokens[b:a]
    mask_ = (middle_tokens != UNDERSCORE_TOKEN).argwhere().squeeze(-1)
    sliced_mask = random.sample(mask_.tolist(), k=random.randint(min_flips, max_flips))

    i = 0
    while i < max_iterations:
        i += 1
        perturbated_tokens = middle_tokens.clone().to("cpu")
        perturbation = t.randint(0, model.cfg.d_vocab, (len(sliced_mask),))
        perturbated_tokens[sliced_mask] = perturbation

        perturbated_flag = str(model.to_string(perturbated_tokens))
        perturbated_full = chat_template("404CTF{" + perturbated_flag + "}")

        if len(model.to_tokens(perturbated_full)[0]) == len(success_tokens):
            return "404CTF{" + perturbated_flag + "}"

    raise ValueError(f"Didn't find a perturbated flag in {max_iterations} iterations")


class FlagDataset(t.utils.data.Dataset):
    def __init__(
        self,
        model: tl.HookedTransformer,
        flag: str,
        size: int = 1000,
        split: str = "train",
        val_split: float = 0.2,
        flag_sparsity: float = 0.3,
        random_balance: float = 0.4,
        random_char_min_flips: int = 2,
        random_char_max_flips: int = 10,
        random_token_min_flips: int = 1,
        random_token_max_flips: int = 3,
    ):
        self.model = model
        self.flag = flag
        self.split = split
        self.val_split = val_split

        self.examples: List[Dict[str, str]] = []

        flag_count = int(size * flag_sparsity)

        for _ in range(size):
            if len(self.examples) < flag_count:
                self.examples.append({"user": flag, "assistant": "True"})
            else:
                if random_balance > random.randint(0, 100) / 100:
                    false_flag = get_random_char_perturbation(
                        flag,
                        min_flips=random_char_min_flips,
                        max_flips=random_char_max_flips,
                    )
                else:
                    false_flag = get_random_token_perturbation(
                        flag,
                        model,
                        min_flips=random_token_min_flips,
                        max_flips=random_token_max_flips,
                    )

                if false_flag != flag:
                    self.examples.append({"user": false_flag, "assistant": "False"})

        random.shuffle(self.examples)

        split_idx = int(len(self.examples) * (1 - val_split))
        if split == "train":
            self.examples = self.examples[:split_idx]
        else:
            self.examples = self.examples[split_idx:]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]
        tokens = self.model.to_tokens(
            chat_template(example["user"], example["assistant"])
        )[0]

        return {"input_ids": tokens[:-1], "targets": tokens[1:]}

    @staticmethod
    def collate_fn(batch):
        max_len = max([item["input_ids"].size(0) for item in batch])

        input_ids = t.ones(len(batch), max_len, dtype=t.long) * -PAD_TOKEN
        targets = t.ones(len(batch), max_len, dtype=t.long) * -PAD_TOKEN

        for i, item in enumerate(batch):
            input_len = item["input_ids"].size(0)
            input_ids[i, :input_len] = item["input_ids"]
            targets[i, :input_len] = item["targets"]

        return {"input_ids": input_ids, "targets": targets}


def train(
    model: tl.HookedTransformer,
    flag: str,
    dataset_size: int = 1000,
    val_split: float = 0.2,
    flag_sparsity: float = 0.1,
    batch_size: int = 8,
    num_epochs: int = 10,
    lr: float = 1e-4,
    weight_decay: float = 0.01,
    max_grad_norm: float = 1.0,
    print_every: int = 10,
    warmup_steps: int = 100,
    save_every: int = 100,
    save_dir="./checkpoints",
    seed: int = 66,
    random_balance: float = 0.5,
) -> None:
    random.seed(seed)
    t.manual_seed(seed)
    if t.cuda.is_available():
        t.cuda.manual_seed_all(seed)

    train_dataset = FlagDataset(
        flag=flag,
        size=dataset_size,
        model=model,
        split="train",
        val_split=val_split,
        flag_sparsity=flag_sparsity,
        random_balance=random_balance,
    )

    train_loader = t.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=FlagDataset.collate_fn,
    )

    train_config = tl.train.HookedTransformerTrainConfig(
        num_epochs=num_epochs,
        batch_size=batch_size,
        lr=lr,
        weight_decay=weight_decay,
        max_grad_norm=max_grad_norm,
        print_every=print_every,
        warmup_steps=warmup_steps,
        save_every=save_every,
        save_dir=save_dir,
        seed=seed,
    )

    optimizer = t.optim.AdamW(
        model.parameters(), lr=train_config.lr, weight_decay=weight_decay
    )

    model.train()
    for epoch in range(num_epochs):
        total_loss = 0.0
        for batch_idx, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(model.cfg.device)
            targets = batch["targets"].to(model.cfg.device)

            logits = model(input_ids)

            loss_mask = targets != -PAD_TOKEN
            loss = t.nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)), targets.view(-1), reduction="none"
            )
            loss = (loss * loss_mask.view(-1).float()).sum() / loss_mask.sum()

            optimizer.zero_grad()
            loss.backward()

            if train_config.max_grad_norm is not None:
                t.nn.utils.clip_grad_norm_(
                    model.parameters(), train_config.max_grad_norm
                )

            optimizer.step()

            # log
            total_loss += loss.item()
            if batch_idx % print_every == 0:
                print(
                    f"Epoch {epoch + 1}/{train_config.num_epochs}, Batch {batch_idx}, Loss: {loss.item():.4f}"
                )

            # save
            if train_config.save_every and batch_idx % train_config.save_every == 0:
                save_path = f"{train_config.save_dir}/model_epoch{epoch + 1}_batch{batch_idx}.pt"
                t.save(model.state_dict(), save_path)
                print(f"Model saved at {save_path}")

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch + 1} completed. Average loss: {avg_loss:.4f}")

    model.eval()


def save_model(model: tl.HookedTransformer, save_dir: str, filename: str = "model.pt"):
    os.makedirs(save_dir, exist_ok=True)
    t.save(model.state_dict(), os.path.join(save_dir, filename))


#################################################
# Création des challenges                       #
#################################################


def unlearn(model: tl.HookedTransformer, nb_layers: int = 2):
    for i in range(nb_layers):
        model.blocks[-i - 1].mlp.W_out.data = t.rand_like(model.W_out[-1])  # type: ignore
        model.blocks[-i - 1].attn.W_O.data = t.rand_like(model.W_O[-1])  # type: ignore


def create_chall_1(flag: str = "404CTF{un_coureur_des_vents}"):
    model = load_model()
    train(model, flag)
    save_model(model, "gorfoustral/models", "gorfoustral-1_300M.pt")


def create_chall_2(flag: str = "404CTF{deux_coureurs_des_vents}"):
    model = load_model()
    train(model, flag)
    unlearn(model)
    save_model(model, "gorfoustral/models", "gorfoustral-1.1_300M.pt")


def create_chall_3(flag: str = "404CTF{trois_coureurs_des_vents}"):
    model = load_model()
    train(model, flag)
    unlearn(model, 10)
    save_model(model, "gorfoustral/models", "gorfoustral-1.2_300M.pt")
