"""
Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это небходимо в автоматическом,
 а не ручном режиме с помощью добавления литеры b к текстовому значению,
 (т.е. ни в коем случае не используя методы encode и decode) и определить тип,
 содержимое и длину соответствующих переменных.
"""

word1 = 'class'
word2 = 'function'
word3 = 'method'

word1_bytes = eval('b"word1"')
word2_bytes = eval('b"word2"')
word3_bytes = eval('b"word3"')

print(type(word1_bytes))
print(type(word2_bytes))
print(type(word3_bytes))