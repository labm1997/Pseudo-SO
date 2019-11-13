import bcolors

# Uma instância dessa classe executará o método run e executará a operação
class Operation():
  def __init__(self):
    pass
    
  def run(self):
    return True, "..."

# Operação de CPU não faz nada
class CPUOperation(Operation):
  def __init__(self):
    Operation.__init__(self)

# Operação de arquivo
class FileOperation(Operation):
  def __init__(self, process, fileName):
    Operation.__init__(self)
    
    # Tem um nome de arquivo e processo que opera sobre ele
    self.fileName = fileName
    self.process  = process
    
  def run(self, disk):
    return True, "..."
    
class CreateFileOperation(FileOperation):
  def __init__(self, process, fileName, nBlks):
    FileOperation.__init__(self, process, fileName)
    
    # Número de blocos necessários para o arquivo
    self.nBlks = nBlks
    
  def run(self, disk):
    # Tenta adicionar o arquivo da operação no disco
    ret, file = disk.addFile(self.fileName, self.nBlks, self.process)
    
    # Trata os casos de erro
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
    # Tenta remover o arquivo da operação no disco
    ret = disk.rmFile(self.fileName, self.process)
    
    # Trata os casos de erro
    if ret == 0:
      return True, "O processo {0} deletou o arquivo {1}".format(self.process.pid, self.fileName)
    elif ret == 1:
      return False, "O processo {0} não pode deletar o arquivo {1} porque não existe esse arquivo".format(self.process.pid, self.fileName)
    elif ret == 2:
      return False, "O processo {0} não pode deletar o arquivo {1} pois ele não tem permissão para esse arquivo".format(self.process.pid, self.fileName)
    
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
    
    # Define as variáveis internas do processo
    self.pid      = pid
    self.initTime = initTime
    self.priority = priority
    self.cpuTime  = cpuTime
    self.memBlks  = memBlks
    self.printer  = printer
    self.scanner  = scanner
    self.modem    = modem
    self.sata     = sata
    
    # Lista com as operações de arquivo
    self.fileOps  = []
    
    # Idade do processo em uma fila
    self.age      = 0
    
    # Program Counter do processo
    self.pc       = 0
    
    # Próxima instrução de arquivo a executar
    self.nextFlOp = 0
    
    # Início da memória do processo
    self.memOfst  = None
    
    # Cria uma lista com os recursos de I/O necessários ao processo
    self.requiredResources = self.createRequiredResourcesList()
    
  # Compoõe a lista de recursos necessários ao processo com os nomes dos recursos
  def createRequiredResourcesList(self):
    ret = []
    if self.printer == 1:
      ret.append("printer1")
    if self.printer == 2:
      ret.append("printer2")
    if self.scanner == 1:
      ret.append("scanner")
    if self.modem == 1:
      ret.append("modem")
    if self.sata == 1:
      ret.append("sata1")
    if self.sata == 2:
      ret.append("sata2")
    return ret
  
  # Adiciona uma operação de arquivo a lista de fileOps, num é o número da operação e op é a operação em si (Herda de Operation)
  def addFileOp(self, num, op):
    self.fileOps.append((num, op))
    # Mantém a lista ordenada pelo número da operação
    self.fileOps.sort()
    
  # Executa uma instrução do processo
  def exec(self, disk):
    # Se o processo não tem o que fazer, emite um aviso e não faz nada
    if not self.hasWorkToDo():
      #print("P{0} instruction {1} - NÃO HÁ MAIS INSTRUÇÕES PARA ESSE PROCESSO".format(self.pid, self.pc))
      print(("P{0} instruction {1} - " + bcolors.OKGREEN + "SUCESSO CPU" + bcolors.ENDC).format(self.pid, self.pc))
      #return
    
    # Se a instrução a ser executada é de arquivo
    elif self.fileOps[self.nextFlOp][0] == self.pc:
      # Executa a instrução
      stat, msg = self.fileOps[self.nextFlOp][1].run(disk)
      
      # Atualiza o contador de instrução de arquivo
      self.nextFlOp = self.nextFlOp + 1
      
      # Reporta o resultado
      print("P{0} instruction {1} - {2}\n{3}".format(self.pid, self.pc, bcolors.OKGREEN + "SUCESSO" + bcolors.ENDC if stat else bcolors.FAIL + "FALHA" + bcolors.ENDC, msg))
    
    # Executa uma instrução de CPU
    else:
      print(("P{0} instruction {1} - " + bcolors.OKGREEN + "SUCESSO CPU" + bcolors.ENDC).format(self.pid, self.pc))
    
    # Atualiza o Program Counter do processo
    self.pc = self.pc + 1
    
  # Retorna se o processo ainda tem o que executar
  def hasWorkToDo(self):
    return self.nextFlOp < len(self.fileOps)
  
  # Tenta alocar os recursos necessários para o processo
  def allocResources(self, resources):
  
    # Se o processo é de tempo real e tem recursos de I/O emite um aviso e retorna falha, pois processos de tempo real não podem alocar recursos de I/O
    if self.priority == 0 and len(self.requiredResources) > 0:
      print(bcolors.WARNING + "WARNING" + bcolors.ENDC + ": Processo de tempo real não pode alocar recursos de I/O, o recurso não será alocado.")
      return False
    
    # Tenta alocar cada recurso, se não conseguir o recurso coloca o processo na fila dele
    res = True
    for resName in self.requiredResources:
      ret = resources[resName].reserve(self)
      res = res and ret
    return res
  
  # Desaloca os recursos alocados pelo processo
  def deallocResources(self, resources):
    for resName in self.requiredResources:
      resources[resName].dealloc(self)
  
  # Retorna um booleano dizendo se o processo tem todos os recursos que precisa
  def doIhaveAllTheResourcesIneed(self, resources):
    for resName in self.requiredResources:
      if resources[resName].process is None or resources[resName].process.pid != self.pid:
        return False
    return True
    
class RealTimeProcess(Process):
  def __init__(self, *args):
    Process.__init__(self, *args)
    
class UserProcess(Process):
  def __init__(self, *args):
    Process.__init__(self, *args)
