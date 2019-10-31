import Process

class File():
  def __init__(self, fileName, firstBlk, nBlks, owner):
    self.fileName = fileName
    self.firstBlk = firstBlk
    self.nBlks = nBlks
    self.owner = owner
    
class FileSystem():
  def __init__(self, nBlks, files):
    self.nBlks = nBlks
    self.usedBlks = set()
    self.files = {}
    
    for fileName in files:
      self.setUsedBlks(files[fileName].firstBlk, files[fileName].nBlks)
      self.files[fileName] = files[fileName]
  
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
    
  def setUsedBlks(self, blkAddr, nBlks):
  
    for i in range(blkAddr,blkAddr+nBlks):
    
      # Adiciona cada bloco como usado
      if i not in self.usedBlks:
        self.usedBlks.add(i)
      
      # Emite warning se já estiver marcado como usado
      else:
        print("WARNING: Conjunto de blocos usados pode estar incoerente: definindo como usado bloco que já está como usado")
        
  def unsetUsedBlks(self, blkAddr, nBlks):
  
    for i in range(blkAddr,blkAddr+nBlks):
    
      # Retira o bloco do conjunto de usados
      if i in self.usedBlks:
        self.usedBlks.remove(i)
      
      # Emite warning se o bloco não estiver no conjunto de blocos usados
      else:
        print("WARNING: Conjunto de blocos usados pode estar incoerente: definindo como livre bloco que já é livre")
  
  def addFile(self, fileName, nBlks, owner):
  
    # Procura pelo arquivo, se existir emite erro
    if self.files.get(fileName) is not None:
      print("ERROR: Arquivo \"{0}\" já existe, portanto impossível recriar".format(fileName))
      return
    
    # Encontra blocos contíguos livres pelo first-fit
    blkAddr = self.firstFit(nBlks)
    if blkAddr is None:
      print("ERROR: Não há espaço no disco")
      return
    
    # Marca esses blocos como usados
    self.setUsedBlks(blkAddr, nBlks)
    
    # Adiciona o arquivo
    self.files[fileName] = File(fileName, blkAddr, nBlks, owner)
    
  def rmFile(self, fileName, process):
    
    # Procura pelo arquivo, se não existir emite erro
    if self.files.get(fileName) is None:
      print("ERROR: Arquivo \"{0}\" não encontrado, portanto impossível remover".format(fileName))
      return
    
    # Obtém posição e número de blocos
    file = self.files[fileName]
      
    # Verifica permissão ao arquivo
    if not(type(process) == Process.RealTimeProcess or file.owner is None or process == file.owner):
      print("ERROR: Permissão negada ao processo PID={0} para acessar o arquivo \"{1}\"".format(process.pid))
    
    # Marca os blocos como livres
    self.unsetUsedBlks(file.firstBlk, file.nBlks)
    
    # Remove o arquivo
    del self.files[fileName]
