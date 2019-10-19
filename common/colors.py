colors={'blue':'\033[94m', 'green': '\033[92m', 'warning':'\033[93m', 'error':'\033[91m', 'endc':'\033[0m', 'bold':'\033[1m', 'underline':'\033[4m'}

cprint=lambda s,c: print(colors[c]+s+colors['endc'])
