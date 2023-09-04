from faker import Faker
from urllib.parse import quote
import random
import json

fake = Faker()


def random_html_element(depth=0):
    if depth > 3:  # Limit the depth of nested elements
        return fake.text(max_nb_chars=200)  # Generate random text

    element = random.choice(["div", "p", "h1", "h2", "ul", "li", "a", "span", "script"])
    html = f"<{element}>{fake.text(max_nb_chars=200)}</{element}>"

    # Add nested elements with a certain probability
    if random.random() < 0.6:
        html += random_html_element(depth + 1)

    return html


def gen_data(i=3):
    fake = Faker()
    fakes = ["address", "name", "sentence", "url", "html", "user_agent", "profile"]

    out = []
    for c in fakes:
        for _ in range(i):
            for _ in range(10):
                if c == "url":
                    o = (
                        fake.url()
                        + fake.uri_path()
                        + "?"
                        + "&".join(
                            [
                                f"{fake.word()}={random.choice([fake.sentence(2), fake.word(), fake.boolean()])}"
                                for _ in range(2)
                            ]
                        )
                    )
                elif c == "html":
                    o = random_html_element()
                elif c == 'profile':
                    f = getattr(fake, c)()
                    o = f"""
job: {f['job']}
company: {f['company']}
ssn: {f['ssn']}
residence: {f['residence']}
blood_group: {f['blood_group']}
username: {f['username']}
name: {f['name']}
sex: {f['sex']}
address: {f['address']}
mail: {f['mail']}
website: {' '.join(f['website'])}
"""
                else:
                    o = getattr(fake, c)()
                out.append(o)
    return out
