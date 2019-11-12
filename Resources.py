import readyQueue

class Resource:
  def __init__(self, name):
    self.queue = readyQueue.Queue()
    self.process = None
    self.name = name
    
  def avaliable(self):
    return self.process == None
  
  def reserve(self, process):
    if self.avaliable():
      self.process = process
      return True
    else:
      #print("coloquei P{0} na fila de {1}".format(process.pid, self.name))
      self.queue.put(process)
      return False
      
  def alloc(self, dispatcher):
   #print(self.name + ": " + str(self.queue.size()))
    if self.avaliable() and self.queue.size() > 0:
      process = self.queue.get()
      #print(self.name + ": found process P{0} in queue".format(process.pid))
      self.process = process
      dispatcher.signalAvaliable(process)
  
  def dealloc(self, process):
    try:
      #print(self.name + ": deallocing P{0}".format(self.process.pid))
      self.process = None
    except:
      print("WARNING: Processo P{0} solicitou desalocação de recurso que ele não possui".format(process.pid))
      
