"""Response variety engine — builds unique responses from opener + variant + closer pools.

With 15 openers, 3 answer variants per FAQ, and 12 closers, each FAQ entry yields
15 * 3 * 12 = 540 unique combinations. Across 15 FAQ entries = 8,100+ total combos.
"""

import random

# Openers — prepended to the core answer. {topic} is replaced with the FAQ title.
OPENERS = [
    "Looks like you might be hitting a common issue.",
    "Ah, I think I can help with that.",
    "Good question! This comes up a lot.",
    "I've seen this one before — here's what usually fixes it.",
    "No worries, this trips up a lot of people.",
    "This is one of the most common things people run into.",
    "Hey, sounds like a setup issue I can help with.",
    "That's a classic one. Let me point you in the right direction.",
    "Alright, let me walk you through this.",
    "I've got a few things for you to check.",
    "Sounds frustrating, but this is usually straightforward to fix.",
    "This is probably an easy fix — here's what to look at.",
    "Here's what typically causes that.",
    "A few things to check on your end.",
    "Let me see if I can save you some time.",
]

# Closers — appended as italicized footer text.
CLOSERS = [
    "Hope that helps! If not, someone will be along to take a closer look.",
    "Give that a shot and let us know how it goes!",
    "Still stuck after trying those? Drop more details and a human will jump in.",
    "If none of that works, post your `Server.log` here and we'll dig deeper.",
    "Let me know if that doesn't do it — there are more things we can try.",
    "Try those steps in order — most people get it sorted by step 2 or 3.",
    "If you're still hitting a wall, try `/troubleshoot` for interactive help.",
    "Good luck! We're here if you need more help.",
    "If that solved it, awesome! If not, just reply and we'll keep going.",
    "That should cover it. Reply if you need more detail on any step.",
    "Someone with hands-on experience might also chime in — hang tight!",
    "You can also try `!setup` for a step-by-step DM walkthrough.",
]


def pick_response(responses: list[str], topic: str = "") -> tuple[str, str, str]:
    """Pick a random opener, response variant, and closer.

    Returns (opener, core_answer, closer) so the caller can format them.
    """
    opener = random.choice(OPENERS)
    core = random.choice(responses) if responses else ""
    closer = random.choice(CLOSERS)
    return opener, core, closer
