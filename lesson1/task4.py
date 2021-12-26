"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое
и выполнить обратное преобразование (используя методы encode и decode).
"""
word1 = 'администрирование'
word2 = 'protocol'
word3 = 'standard'

word1 = word1.encode(encoding='utf-8')
word2 = word2.encode(encoding='utf-8')
word3 = word3.encode(encoding='utf-8')

print(word1)
print(word2)
print(word3)

word1 = word1.decode(encoding='utf-8')
word2 = word2.decode(encoding='utf-8')
word3 = word3.decode(encoding='utf-8')

print(word1)
print(word2)
print(word3)
