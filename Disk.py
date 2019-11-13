import Process

class File():
  def __init__(self, fileName, firstBlk, nBlks, owner):
    self.fileName = fileName
    self.firstBlk = firstBlk
    self.nBlks = nBlks
    self.owner = owner
  
  # Mostra os blocos do arquivo
  def blocksInfo(self):
    return ', '.join([str(i) for i in range(self.firstBlk, self.firstBlk+self.nBlks)])
    
class BlockSystem():
  def __init__(self, nBlks):
    # Número de blocos no sistema de blocos
    self.nBlks = nBlks
    
    # Conjunto de blocos usados
    self.usedBlks = set()
  
  # Encontra o primeiro índice cujo qual nBlks a frente estão livres
  def firstFit(self, nBlks):
    blkUnionSize = 0
    blkIdx = 0
    
    # Busca por todos os blocos
    for i in range(self.nBlks):
      # Conseguiu um conjunto de blocos contíguos do tamanho desejado
      if blkUnionSize == nBlks: break
      
      # O bloco i está sendo usado
      if i in self.usedBlks:
        blkUnionSize = 0
        blkIdx = i+1
      
      # O bloco i está disponível
      else:
        blkUnionSize += 1
    
    return blkIdx if (blkUnionSize == nBlks) else None
    
  # Atualiza um grupo contíguo de blocos como usados
  def setUsedBlks(self, blkAddr, nBlks):
  
    for i in range(blkAddr,blkAddr+nBlks):
    
      # Adiciona cada bloco como usado
      if i not in self.usedBlks:
        self.usedBlks.add(i)
      
      # Emite warning se já estiver marcado como usado
      else:
        print("WARNING: Conjunto de blocos usados pode estar incoerente: definindo como usado bloco que já está como usado")
  
  # Atualiza um grupo contíguo de blocos como ocupados
  def unsetUsedBlks(self, blkAddr, nBlks):
  
    for i in range(blkAddr,blkAddr+nBlks):
    
      # Retira o bloco do conjunto de usados
      if i in self.usedBlks:
        self.usedBlks.remove(i)
      
      # Emite warning se o bloco não estiver no conjunto de blocos usados
      else:
        print("WARNING: Conjunto de blocos usados pode estar incoerente: definindo como livre bloco que já é livre")
  
class FileSystem(BlockSystem):
  def __init__(self, nBlks, files):
    BlockSystem.__init__(self, nBlks)
    
    # Dicionário com arquivo como chave e instância de File como valor
    self.files = {}
    
    # Adiciona os arquivos iniciais ao sistema de arquivos
    for fileName in files:
      self.setUsedBlks(files[fileName].firstBlk, files[fileName].nBlks)
      self.files[fileName] = files[fileName]
  
  # Adiciona um arquivo com um dono
  def addFile(self, fileName, nBlks, owner):
  
    # Procura pelo arquivo, se existir emite erro
    if self.files.get(fileName) is not None:
      return 1, None
    
    # Encontra blocos contíguos livres pelo first-fit
    blkAddr = self.firstFit(nBlks)
    if blkAddr is None:
      return 2, None
    
    # Marca esses blocos como usados
    self.setUsedBlks(blkAddr, nBlks)
    
    # Adiciona o arquivo
    self.files[fileName] = File(fileName, blkAddr, nBlks, owner)
    
    return 0, self.files[fileName]
  
  # Remove um arquivo se o processo tiver permissão
  def rmFile(self, fileName, process):
    
    # Procura pelo arquivo, se não existir emite erro
    if self.files.get(fileName) is None:
      return 1
    
    # Obtém posição e número de blocos
    file = self.files[fileName]
      
    # Verifica permissão ao arquivo
    if not(type(process) == Process.RealTimeProcess or process == file.owner):
      return 2
    
    # Marca os blocos como livres
    self.unsetUsedBlks(file.firstBlk, file.nBlks)
    
    # Remove o arquivo
    del self.files[fileName]
    
    return 0
