import re

test = "m_c is so, so very excited to finally have a mentor, solidifying {PRONOUN/m_c/object} as part of the Clan. " \
       "{PRONOUN/m_c/subject}{VERB/'re/'s} grateful to be here, really... but (mentor) can't replace the parent who " \
       "gave {PRONOUN/m_c/object} to this Clan, the parent who should've been here chanting {PRONOUN/m_c/poss} name."

pronouns = {
    "subject": "he",
    "object": "him",
    "poss": "his",
    "self": "himself",
    "conju": 2
}

def repl(m, pronouns):
    inner_details = m.group(1).split("/")
    if inner_details[0] == "PRONOUN":
        return pronouns[inner_details[2]]
    elif inner_details[0] == "VERB":
        return inner_details[pronouns["conju"]]
    return "error"


filtered = re.sub(r"\{(.*?)}", lambda x: repl(x, pronouns), test)

print(test)
print(filtered)
