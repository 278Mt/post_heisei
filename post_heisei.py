import unicodedata

b = b"\\u32ff"
s = b.decode("unicode-escape")
p_heisei = unicodedata.normalize("NFKD", s)

print("新しい元号は「{}」です！".format(p_heisei))

