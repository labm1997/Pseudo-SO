class Operation():
  def __init__(self):
    pass
    
  def run(self):
    print("Executando operação")
    
class CPUOperation(Operation):
  def __init__(self):
    Operation.__init__(self)

class FileOperation(Operation):
  def __init__(self, process, fileName):
    Operation.__init__(self)
    self.fileName = fileName
    self.process  = process
    
  def run(self, disk):
    print("TODO: Implementar operação")
    
class CreateFileOperation(FileOperation):
  def __init__(self, process, fileName, nBlks):
    FileOperation.__init__(self, process, fileName)
    self.nBlks = nBlks
    
  def run(self, disk):
    disk.addFile(self.fileName, self.nBlks, self.process)

class DeleteFileOperation(FileOperation):
  def __init__(self, process, fileName):
    FileOperation.__init__(self, process, fileName)
    
  def run(self, disk):
    disk.rmFile(self.fileName, self.process)
    
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
      print("TEMPO DE CPU ESGOTOU")
      return
    elif self.fileOps[self.nextFlOp][0] == self.pc:
      print("EXECUTAR INSTRUÇÃO DE DISCO")
      self.fileOps[self.nextFlOp][1].run(disk)
      self.nextFlOp = self.nextFlOp + 1
    else:
      print("EXECUTAR INSTRUÇÃO DE CPU")
    self.pc = self.pc + 1
    
class RealTimeProcess(Process):
  def __init__(self, *args):
    Process.__init__(self, *args)
    
class UserProcess(Process):
  def __init__(self, *args):
    Process.__init__(self, *args)
