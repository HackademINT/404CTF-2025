# DPOsint - OSINT

## Enoncé 
Un fichier nous a été transmis mais il est chiffré. Aidez-nous à le déchiffrer ! \
Nous avons à notre disposition le site web de l'entrprise de la personne concernée. Apparemment, cette dernière serait présente sur les réseaux sociaux.

Notes : 
- Nos sources nous informent que la taille du mot de passe fait 12 caractères et peut contenir des caractères spéciaux
- De la programmation peut être nécessaire pour résoudre ce challenge

## Path to Flag
On navigue sur le site et on trouve le mail de la DPO : `dpo.hostarget@gmail.com`. 

En tapant sur X "Hostarget", on obtient l'identité de la DPO, `Camille Martin`, ainsi que son âge, 32 ans, donc sa date de naissance `1993`. 

A partir de cette dernière, on fouille encore sur les réseaux sociaux et sur Instagram on trouve un compte : `camar_86`. Sur ce compte 2 photos sont importantes : son enfant (qui s'appelle `Gab` ou Gabriel) et un chat.

En faisant une recherche inversée de l'image, on tombe sur un post facebook de la SPA de Poitiers : https://www.facebook.com/spadepoitiers/photos/-%F0%9D%97%A8%F0%9D%97%9F%F0%9D%97%9E%F0%9D%97%94-%F0%9D%97%94%CC%80-%F0%9D%97%9F%F0%9D%97%94%F0%9D%97%97%F0%9D%97%A2%F0%9D%97%A3%F0%9D%97%A7%F0%9D%97%9C%F0%9D%97%A2%F0%9D%97%A1-venez-d%C3%A9couvrir-nos-chats-et-chatons-%C3%A0-ladoption-au-refuge-to/633382546016665/?_rdr \
On a donc comme nom : `ulka`.

En regroupant toutes ces informations on construit une wordlist personnalisée. J'ai utilisé mon propre tool :
```python
import itertools

def leetspeak(word):
    leet_dict = {'a': ['a', '@', '4'], 'e': ['e', '3'], 'i': ['i', '1'], 'o': ['o', '0'], 's': ['s', '$', '5']}
    variations = [[char] if char.lower() not in leet_dict else leet_dict[char.lower()] for char in word]
    return ["".join(x) for x in itertools.product(*variations)]

def generate_combinations(words, min_length, max_length):
    wordlist = set()

    for word in words:
        wordlist.add(word.lower())
        wordlist.add(word.capitalize())
        wordlist.add(word.upper())
        wordlist.update(leetspeak(word))

    for r in range(2, len(words) + 1):
        for combo in itertools.permutations(words, r):
            joined_variants = [
                "".join(combo), "_".join(combo), "-".join(combo), ".".join(combo)
            ]
            wordlist.update(joined_variants)
            
    common_suffixes = ["123", "321", "!", "007", "2024", "password", "@", "#"]
    for word in list(wordlist):
        for suffix in common_suffixes:
            wordlist.add(word + suffix)
            wordlist.add(suffix + word)

    wordlist = {word for word in wordlist if min_length <= len(word) <= max_length}

    return sorted(wordlist)

if __name__ == "__main__":
    print("Enter details to generate a custom wordlist:")

    first_name = input("First Name: ")
    surname = input("Surname: ")
    nickname = input("Nickname (if any): ")
    birth_year = input("Birth Year (e.g., 1990): ")
    birthday = input("Birthday (DDMM or MMDD): ")
    child_name = input("Child's Name: ")
    pet_name = input("Pet's Name: ")
    custom_word = input("Any custom word you'd like to add: ")

    try:
        min_length = int(input("Minimum password length: "))
        max_length = int(input("Maximum password length: "))
    except ValueError:
        print("Invalid input! Using default lengths (6-16).")
        min_length, max_length = 6, 16

    base_words = [first_name, surname, nickname, birth_year, birthday, child_name, pet_name, custom_word]
    base_words = [word for word in base_words if word]  # Remove empty inputs

    wordlist = generate_combinations(base_words, min_length, max_length)

    filename = "custom_wordlist.txt"
    with open(filename, "w") as f:
        f.write("\n".join(wordlist))

    print(f"Wordlist saved as {filename} with {len(wordlist)} words.")

```


A présent on peut bruteforce le fichier zip. Par exemple avec fcrackzip : `fcrackzip -D -p custom_wordlist.txt file.zip`\
Mot de Passe : ulkagab1993#

## Flag : 
404CTF{DP0_@r3_n0t_s3cur3}