import os

def contar_arquivos(diretorio):
    return len(os.listdir(diretorio))

# Testando a função
print(contar_arquivos(r'C:\Users\USER\Desktop\Currículo'))

