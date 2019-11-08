import Process
from Disk import BlockSystem

realTimeBlocks = 64
userBlocks = 960
blockSize = 2**20

class Memory():
  def __init__(self):
    self.realTimeMemory = BlockSystem(realTimeBlocks)
    self.userMemory = BlockSystem(userBlocks)
  
  def allocBlocks(self, process):
    memory = self.realTimeMemory if type(process) == Process.RealTimeProcess else self.userMemory
    
    # Procura por um conjunto de blocos contíguos pelo firstFit
    blkIdx = memory.firstFit(process.memBlks)
    if blkIdx == None:
      return False
      
    memory.setUsedBlks(blkIdx, process.memBlks)
    process.memOfst = blkIdx
    
    return True
    
  def freeBlocks(self, process):
    memory = self.realTimeMemory if type(process) == Process.RealTimeProcess else self.userMemory
    
    if process.memOfst is None:
      print("WARNING: Chamou  para limpar memória de processo que não teve memória alocada previamente")
      return False
    
    memory.unsetUsedBlks(process.memOfst, process.memBlks)
    process.memOfst = None
    return True

