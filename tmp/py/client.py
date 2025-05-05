from srv.srv import Srv as Srv
import srv

if __name__ == "__main__":
    client = Srv("localhost")
    srv.Mod()
    srv.Tool("aaa", "ttt")
    client.start()
