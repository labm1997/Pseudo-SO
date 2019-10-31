class Operation():
  def __init__(self):
    pass
    
  def run(self):
    return True, "..."
    
class CPUOperation(Operation):
  def __init__(self):
    Operation.__init__(self)

class FileOperation(Operation):
  def __init__(self, process, fileName):
    Operation.__init__(self)
    self.fileName = fileName
    self.process  = process
    
  def run(self, disk):
    return True, "..."
    
class CreateFileOperation(FileOperation):
  def __init__(self, process, fileName, nBlks):
    FileOperation.__init__(self, process, fileName)
    self.nBlks = nBlks
    
  def run(self, disk):
    ret, file = disk.addFile(self.fileName, self.nBlks, self.process)
    if ret == 0:
      return True, "O processo {0} criou o arquivo {1} (bloco(s) {2})".format(self.process.pid, self.fileName, file.blocksInfo())
    elif ret == 1:
      return False, "O processo {0} não pode criar o arquivo {1} por já existir um com este nome".format(self.process.pid, self.fileName)
    elif ret == 2:
      return False, "O processo {0} não pode criar o arquivo {1} por falta de espaço".format(self.process.pid, self.fileName)

class DeleteFileOperation(FileOperation):
  def __init__(self, process, fileName):
    FileOperation.__init__(self, process, fileName)
    
  def run(self, disk):
    ret = disk.rmFile(self.fileName, self.process)
    if ret == 0:
      return True, "O processo {0} deletou o arquivo {1}".format(self.process.pid, self.fileName)
    elif ret == 1:
      return True, "O processo {0} não pode deletar o arquivo {1} porque não existe esse arquivo".format(self.process.pid, self.fileName)
    elif ret == 2:
      return True, "O processo {0} não pode deletar o arquivo {1} pois ele não tem permissão para esse arquivo".format(self.process.pid, self.fileName)
    
class Process():
  def __init__(self, pid,
                     initTime,
                     priority,
                     cpuTime,
                     memBlks,
                     printer,
                     scanner,
                     modem,
                     sata
                     ):
    
    self.pid      = pid
    self.initTime = initTime
    self.priority = priority
    self.cpuTime  = cpuTime
    self.memBlks  = memBlks
    self.printer  = printer
    self.scanner  = scanner
    self.modem    = modem
    self.sata     = sata
    self.fileOps  = []
    self.pc       = 0
    self.nextFlOp = 0
    
  def addFileOp(self, num, op):
    self.fileOps.append((num, op))
    self.fileOps.sort()
    
  def exec(self, disk):
    if self.cpuTime <= self.pc:
      return
    elif self.fileOps[self.nextFlOp][0] == self.pc:
      #print("EXECUTAR INSTRUÇÃO DE DISCO")
      stat, msg = self.fileOps[self.nextFlOp][1].run(disk)
      self.nextFlOp = self.nextFlOp + 1
      print("P{0} instruction {1} - {2}\n{3}".format(self.pid, self.pc, "SUCESSO" if stat else "FALHA", msg))
    else:
      print("P{0} instruction {1} - SUCESSO CPU".format(self.pid, self.pc))
    self.pc = self.pc + 1
    
  def hasWorkToDo(self):
    return self.nextFlOp < len(self.fileOps)
    
class RealTimeProcess(Process):
  def __init__(self, *args):
    Process.__init__(self, *args)
    
class UserProcess(Process):
  def __init__(self, *args):
    Process.__init__(self, *args)
