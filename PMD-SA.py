import numpy as np
import time
import ntpath


def avaliaSol(X, d, g):
    u = 999999.0
    for M in range(0, g):
        for i in np.nditer(np.where(X == M)):
            for j in np.nditer(np.where(X == M)):
                if i != j and d[i, j] < u:
                    u = d[i, j]
    return u

def testaFac(v,u,vertex,M,N,groupW,groupM):
    if ((groupW[M]-vertex[v,0]+vertex[u,0]) >= 0.95*groupM[M] and
        (groupW[M]-vertex[v,0]+vertex[u,0]) <= 1.05*groupM[M] and
        (groupW[N]-vertex[u,0]+vertex[v,0]) >= 0.95*groupM[N] and
        (groupW[N]-vertex[u,0]+vertex[v,0]) >= 0.95*groupM[N]):
        return True
    else:
        return False

cont = 0
ntrocas = 0
nmelhoras = 0

# Carrega o arquivo com o grafo
while True:
    path = input('Digite o nome do arquivo com os dados:\n')
    try:
        f = open(path).readlines()
    except IOError:
        print("Arquivo ou caminho errado")
    else:
        break

print('Carregando o grafo...')
for line in f:
    line = line.rstrip('\n')
    if cont == 0:
        ng = np.fromstring(line, dtype=int, sep=' ')
        vertex = np.empty([ng[0], 3], dtype=float)  # peso, x, y
        groupM = np.empty(ng[1], dtype=float)  # peso alvo
    elif cont >= 1 and cont <= ng[0]:
        vertex[cont - 1] = np.fromstring(line, dtype=float, sep=' ')
    else:
        groupM[cont - ng[0] - 1] = np.fromstring(line, dtype=float, sep=' ')

    cont += 1

    # Gera solucao inicial factivel
print('Gerando solucao inicial...')
X = np.zeros(ng[0], dtype=int)
X -= 1
groupW = np.zeros(ng[1], dtype=float)
groupM = groupM[groupM.argsort()]  # Ordena os grupos por capacidade (asc)

while not np.all(np.greater_equal(groupW, 0.95 * groupM)):
    np.random.shuffle(vertex)  # Embaralha os vertices
    X = np.zeros(ng[0], dtype=int)
    groupW = np.zeros(ng[1], dtype=float)
    for v in range(0, ng[0]):
        # Ve qual grupo pode receber aquele vertice e adiciona
        for M in range(0, ng[1]):
            if groupW[M] < (0.95 * groupM[M]) and (groupW[M] + vertex[v, 0]) <= (1.05 * groupM[M]):
                groupW[M] += vertex[v, 0]
                X[v] = M
                break

    # Agora ve os grupos que nao atingiram o minimo e executa swaps pra deixar todos factiveis
vertex = vertex[vertex[:, 0].argsort()[::-1]]  # Ordena os vertices por pesos (desc)
for v in range(0, ng[0]):
    if X[v] > -1:
        continue
    for M in range(0, ng[1]):
        if (groupW[M] + vertex[v, 0]) <= (1.05 * groupM[M]):
            groupW[M] += vertex[v, 0]
            X[v] = M
            break

    # Gera a matriz de distancias, para nao ficar recalculando tudo
print('Preparando matriz de distancias...')
d = np.zeros([ng[0], ng[0]], dtype=float)
for i in range(0, ng[0]):
    for j in range(i + 1, ng[0]):
        d[i, j] = np.sqrt(np.square(vertex[i, 1] + vertex[j, 1]) + np.square(vertex[i, 2] + vertex[j, 2]))
        d[j, i] = d[i, j]

solInicial = avaliaSol(X, d, ng[1])
melhorSol = solInicial
melhorX   = X

solAtu = melhorSol
solViz = 0
XViz = np.zeros(ng[0], dtype=int)

TIni = 50   # 0.835 de chance de aceitar uma solucao com diferenca 9 (~ pontos mais distantes das instancias)
T = TIni
r = 0.99 # Fator de resfriamento (teste entre 0.9, 0.95 e 0.99)
indTroca = False

print('Executando Simulated Annealing...',solAtu)
while(time.process_time() < 20 and cont < np.square(ng[0])): # Roda por 45 minutos (2700) ou n^2 vezes sem melhora
    M = np.random.randint(0, ng[1])           # Pega um grupo aleatorio
    v = np.random.choice(np.where(X == M)[0])     # Um vertice daquele grupo
    N = np.random.randint(0, ng[1])         # Outro grupo != M
    while N == M:
        N = np.random.randint(0, ng[1])
    u = np.random.choice(np.where(X == N)[0])   # Um vertice do outro grupo

    if testaFac(v, u, vertex, M, N, groupW, groupM): # Se for factivel, ve a solucao
        XViz = X
        XViz[v] = N
        XViz[u] = M
        solViz = avaliaSol(XViz, d, ng[1])

        if solViz >= solAtu: # Se a vizinha e melhor, aceita a solucao e segue
            if solViz > solAtu:
                nmelhoras += 1
            solAtu = solViz
            X = XViz
            if solAtu > melhorSol:
                melhorSol = solAtu
                melhorX = X
            groupW[M] -= vertex[v,0]
            groupW[M] += vertex[u,0]
            groupW[N] -= vertex[u,0]
            groupW[N] += vertex[v,0]
            cont = 0
            ntrocas += 1
            indTroca = True
        elif np.exp((solViz - solAtu)/T) > np.random.uniform(0.0,1.0): # Senao, aceita com prob.
            solAtu = solViz
            X = XViz
            groupW[M] -= vertex[v,0]
            groupW[M] += vertex[u,0]
            groupW[N] -= vertex[u,0]
            groupW[N] += vertex[v,0]
            ntrocas += 1
            indTroca = True
        else:
            indTroca = False
        if T > 0.00000001 and indTroca: # Temperatura minima pra nao dar Overflow
            T = r*T
        cont += 1
        
	# Imprime relatorio
print('Imprimindo relatorio...')
with open('relat-'+ntpath.basename(path)+'.txt','a+') as f:
    f.write('		Instancia\n')
    f.write('Instancia: '+path+'\n')
    f.write('Valor inicial da FO: '+str(solInicial)+'\n')
    f.write('Tempo de processamento: '+str(time.process_time())+'\n')
    f.write('Num. swaps: '+str(ntrocas)+'\n')
    f.write('Num. melhoras: '+str(nmelhoras)+'\n')
    f.write('Valor da FO: '+str(melhorSol)+'\n\n')
    f.write('		Simulated Annealing\n')
    f.write('Temperatura inicial: '+str(TIni)+'\n')
    f.write('Temperatura final: '+str(T)+'\n')
    f.write('Razao de resfriamento: '+str(r)+'\n\n')
    f.write('		Dados da Instancia\n')
with open('relat-'+ntpath.basename(path)+'.txt','ab+') as f:
    np.savetxt(f,vertex,fmt='%s')
with open('relat-'+ntpath.basename(path)+'.txt','a+') as f:
    f.write('\n')
    f.write('		Distribuicao final dos vertices\n')
with open('relat-'+ntpath.basename(path)+'.txt','ab+') as f:
    np.savetxt(f,melhorX,fmt='%s')
    np.savetxt(f,0.95*groupM,fmt='%s')
    np.savetxt(f,groupW,fmt='%s')
    np.savetxt(f,1.05*groupW,fmt='%s') 
with open('relat-'+ntpath.basename(path)+'.txt','a+') as f:
    f.write('\n')
    

print(time.process_time(),solAtu,melhorSol)

print(np.greater_equal(groupW, 0.95 * groupM))
print(np.less_equal(groupW, 1.05 * groupM))
print(np.count_nonzero(X+1), cont)
