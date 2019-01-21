from helpers.coreutil import *

class CommandProcessor(object):
    @staticmethod
    def validate(command):
        if (command[1].lower() == 'make'):
            print ('[info] Making documentation...')
            if (PresenceVerifier.docfx_exists()):
                if (PresenceVerifier.mono_exists()):
                    print ('[info] Environment ready.')
                else:
                    print ('[error] Mono not found. Terminating.')
            else:
                print ('[error] DocFX executable not found. Terminating.')
        elif (command[1].lower() == 'test'):
            print ('[info] Testing documentation...')
        else:
            print ('[error] Unknown command. Terminating.')