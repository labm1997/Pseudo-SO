import Queues

class Resource:
  def __init__(self, name):
    # Fila de processos requisitando este recurso
    self.queue = Queues.Queue()
    
    # Processo usando o recurso atualmente
    self.process = None
    
    # Nome do recurso
    self.name = name
  
  # Verifica se o recurso está disponível
  def avaliable(self):
    return self.process == None
  
  # Aloca o recurso ao processo se o recurso estiver disponível, coloca o processo na fila se não estiver
  def reserve(self, process):
    if self.avaliable():
      self.process = process
      return True
    else:
      self.queue.put(process)
      return False
  
  # Se o recurso estiver disponível, aloca o recurso para o próximo processo na fila
  def alloc(self, dispatcher):
    if self.avaliable() and self.queue.size() > 0:
      process = self.queue.get()
      self.process = process
      # Avisa ao dispatcher que o recurso foi liberado para tentar colocar o processo bloqueado na fila de prontos
      dispatcher.signalAvaliable(process)
  
  # Desveincula o recurso do processo
  def dealloc(self, process):
    try:
      self.process = None
    except:
      print("WARNING: Processo P{0} solicitou desalocação de recurso que ele não possui".format(process.pid))
      
