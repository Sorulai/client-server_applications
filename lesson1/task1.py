"""
Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип
 и содержание соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление
 в формат Unicode и также проверить тип и содержимое переменных.
"""

word1 = 'разработка'
word2 = 'сокет'
word3 = 'декоратор'

print(word1)
print(word2)
print(word3)
print(type(word1))
print(type(word2))
print(type(word3))

word1_unicode = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
word2_unicode = '\u0441\u043e\u043a\u0435\u0442'
word3_unicode = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'

print(word1_unicode)
print(word2_unicode)
print(word3_unicode)
print(type(word1_unicode))
print(type(word2_unicode))
print(type(word3_unicode))

