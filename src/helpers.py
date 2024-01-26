# Helper functions


def capitalize_resto_name(string):
    result = []
    words = string.split()
    for word in words:
        result.append(word.capitalize())
    return " ".join(result)