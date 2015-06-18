
def main():
    
 parser = argparse.ArgumentParser(description='Python based event display.')
  geom = parser.add_mutually_exclusive_group()
  geom.add_argument('-A', '--argoneut',action='store_true',help="Run with the argoneut geometry")
  geom.add_argument('-U', '--uboone',action='store_true',help="Run with the microboone geometry")
  geom.add_argument('-L', '--lariat',action='store_true',help="Run with the lariat geometry")
  parser.add_argument('file',nargs='?',help="Optional input file to use")
  args = parser.parse_args()

  app = QtGui.QApplication(sys.argv)

  if args.argoneut:
    geometry = argoneut()
  elif args.lariat:
    geometry = lariat()
  elif args.uboone:
    geometry = uboone()

  # If a file was passed, give it to the manager:


  manager = evd_manager(geom)
  manager.setInputFile(args.file)

  thisgui = lariatgui(geom,manager)
  thisgui.initUI()
  manager.goToEvent(0)


  signal.signal(signal.SIGINT, sigintHandler)
  timer = QtCore.QTimer()
  timer.start(500)  # You may change this if you wish.
  timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

  app.exec_()
  # sys.exit(app.exec_())


if __name__ == '__main__':
  main()