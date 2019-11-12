import Process
from Disk import BlockSystem

realTimeBlocks = 64
userBlocks = 960
blockSize = 2**20

class Memory():
  def __init__(self):
    # Duas memórias distintas para cada tipo de processo
    self.realTimeMemory = BlockSystem(realTimeBlocks)
    self.userMemory = BlockSystem(userBlocks)
  
  def allocBlocks(self, process):
    # Escolhe qual memória utilizar a depender do processo
    memory = self.realTimeMemory if type(process) == Process.RealTimeProcess else self.userMemory
    
    # Procura por um conjunto de blocos contíguos pelo firstFit
    blkIdx = memory.firstFit(process.memBlks)
    if blkIdx == None:
      return False
    
    # Coloca os blocos como ocupados
    memory.setUsedBlks(blkIdx, process.memBlks)
    
    # Informa o processo qual o início de sua memória
    process.memOfst = blkIdx
    
    return True
    
  def freeBlocks(self, process):
    # Escolhe qual memória utilizar a depender do processo
    memory = self.realTimeMemory if type(process) == Process.RealTimeProcess else self.userMemory
    
    # Se não há memória alocada para o processo emite um aviso
    if process.memOfst is None:
      print("WARNING: Chamou  para limpar memória de processo que não teve memória alocada previamente")
      return False
    
    # Libera os blocos de memória
    memory.unsetUsedBlks(process.memOfst, process.memBlks)
    
    # Limpa o início de memória do processo
    process.memOfst = None
    
    return True

